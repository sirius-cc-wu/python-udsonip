"""
ECU discovery utilities for DoIP networks.
"""

from typing import List, Optional
from dataclasses import dataclass
import time
import warnings
import socket

from doipclient.client import DoIPClient, Parser
from doipclient.messages import (
    VehicleIdentificationRequest,
    VehicleIdentificationResponse,
    payload_message_to_type,
)
from doipclient.constants import UDP_DISCOVERY

from . import exceptions
from .client import UdsOnIpClient


@dataclass
class ECUInfo:
    """Information about a discovered ECU."""

    ip: str
    """IP address of the ECU/gateway"""

    logical_address: int
    """ECU logical address"""

    vin: Optional[str] = None
    """Vehicle Identification Number"""

    eid: Optional[bytes] = None
    """Entity Identification (VIN or similar)"""

    gid: Optional[bytes] = None
    """Group Identification"""

    further_action_required: Optional[int] = None
    """Further action required byte"""

    vin_gid_sync_status: Optional[int] = None
    """VIN/GID Synchronization status"""

    def __str__(self):
        return f"ECU({self.ip} @ 0x{self.logical_address:04X})"

    def __repr__(self):
        return f"ECUInfo(ip='{self.ip}', logical_address=0x{self.logical_address:04X})"

    def connect(self, client_ip: Optional[str] = None, **kwargs):
        """
        Create a UdsOnIpClient connected to this ECU.

        Args:
            client_ip: Optional client IP address
            **kwargs: Additional arguments for UdsOnIpClient

        Returns:
            UdsOnIpClient instance
        """
        return UdsOnIpClient(
            ecu_ip=self.ip,
            ecu_address=self.logical_address,
            client_ip=client_ip,
            protocol_version=0x03,  # Default to 0x03 as per user request
            **kwargs,
        )


def discover_ecus(
    interface: Optional[str] = None, timeout: float = 3.0, protocol_version: int = 0x03
) -> List[ECUInfo]:
    """
    Discover ECUs on the DoIP network by broadcasting a Vehicle Identification
    Request and listening for unicast responses.
    This function implements a more robust discovery method:
    1. Creates a single UDP socket bound to an ephemeral port.
    2. Broadcasts a Vehicle Identification Request.
    3. Listens on the same socket for direct unicast responses from all
       ECUs for the entire timeout period.
    This approach correctly captures all direct responses and is more efficient
    than the previous implementation.
    Args:
        interface: Network interface to use for IPv6 (not typically required for IPv4).
        timeout: Discovery timeout in seconds.
        protocol_version: DoIP protocol version (default: 0x03).
    Returns:
        List of discovered ECU information (duplicates filtered by IP and logical address).
    Raises:
        DiscoveryError: If discovery fails due to network or protocol errors.
    """
    discovered_ecus = []
    seen_ecus = set()  # To store (ip, logical_address) to avoid duplicates
    sock = None

    try:
        # The _create_udp_socket in doipclient handles some of the complexities
        # of binding to a specific interface for IPv6.
        is_ipv6 = False  # Assuming IPv4 for broadcast for now.
        sock = DoIPClient._create_udp_socket(
            ipv6=is_ipv6,
            udp_port=0,  # Bind to an ephemeral port for sending and receiving unicast replies
            timeout=timeout,
            source_interface=interface,
        )
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)

        # Manually construct and send the Vehicle Identification Request
        message = VehicleIdentificationRequest()
        payload_data = message.pack()
        payload_type = payload_message_to_type[type(message)]
        data_bytes = DoIPClient._pack_doip(protocol_version, payload_type, payload_data)

        # Send broadcast request
        sock.sendto(data_bytes, ("255.255.255.255", UDP_DISCOVERY))

        # Listen for responses on the same socket
        start_time = time.time()
        parser = Parser()

        while time.time() - start_time < timeout:
            try:
                remaining_timeout = timeout - (time.time() - start_time)
                if remaining_timeout <= 0:
                    break

                sock.settimeout(remaining_timeout)
                data, addr = sock.recvfrom(1024)  # Buffer size

                # The parser in doipclient is designed to read from a stream,
                # but for UDP each datagram is a full message.
                parser.reset()
                announcement = parser.read_message(data)

                if announcement and isinstance(announcement, VehicleIdentificationResponse):
                    ip, _ = addr
                    logical_address = announcement.logical_address

                    if (ip, logical_address) not in seen_ecus:
                        ecu_info = ECUInfo(
                            ip=ip,
                            logical_address=logical_address,
                            vin=announcement.vin if announcement.vin else None,
                            eid=announcement.eid,
                            gid=announcement.gid,
                            further_action_required=announcement.further_action_required.value,
                            vin_gid_sync_status=(
                                announcement.vin_sync_status.value
                                if announcement.vin_sync_status is not None
                                else None
                            ),
                        )
                        discovered_ecus.append(ecu_info)
                        seen_ecus.add((ip, logical_address))

            except socket.timeout:
                # This is expected when no more responses are coming in
                break
            except Exception as e:
                warnings.warn(f"Error during ECU discovery: {e}", RuntimeWarning)
                continue

        return discovered_ecus

    except Exception as e:
        raise exceptions.DiscoveryError(f"ECU discovery failed: {e}")
    finally:
        if sock:
            sock.close()


def get_entity(ip: str, protocol_version: int = 0x03) -> Optional[ECUInfo]:
    """
    Get entity information from a specific DoIP gateway/ECU.

    Args:
        ip: IP address of the DoIP entity
        protocol_version: DoIP protocol version (default: 0x03)

    Returns:
        ECUInfo if successful, None otherwise

    Example:
        >>> ecu = get_entity('192.168.1.10')
        >>> if ecu:
        ...     print(f"ECU at {ecu.ip}: {ecu.logical_address:#x}")
    """
    try:
        address, announcement = DoIPClient.get_entity(
            ecu_ip_address=ip, protocol_version=protocol_version
        )

        ip_address, _ = address

        return ECUInfo(
            ip=ip_address,
            logical_address=announcement.logical_address,
            vin=announcement.vin if announcement.vin else None,
            eid=announcement.eid,
            gid=announcement.gid,
            further_action_required=announcement.further_action_required.value,
            vin_gid_sync_status=(
                announcement.vin_sync_status.value
                if announcement.vin_sync_status is not None
                else None
            ),
        )
    except TimeoutError:
        return None
    except Exception as e:
        raise exceptions.DiscoveryError(f"Failed to get entity info from {ip}: {e}")
