"""
ECU discovery utilities for DoIP networks.
"""

from typing import List, Optional
from dataclasses import dataclass
import time
import warnings
from doipclient import DoIPClient
from . import exceptions


@dataclass
class ECUInfo:
    """
    Information about a discovered ECU.
    
    Attributes:
        ip: IP address of the ECU/gateway
        logical_address: ECU logical address
        eid: Entity Identification (VIN or similar)
        gid: Group Identification
        further_action: Further action required byte
    """
    ip: str
    logical_address: int
    eid: Optional[bytes] = None
    gid: Optional[bytes] = None
    further_action_required: Optional[int] = None
    
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
        from .client import UdsOnIpClient
        return UdsOnIpClient(
            ecu_ip=self.ip,
            ecu_address=self.logical_address,
            client_ip=client_ip,
            protocol_version=0x03, # Default to 0x03 as per user request
            **kwargs
        )


def discover_ecus(
    interface: Optional[str] = None,
    timeout: float = 5.0,
    protocol_version: int = 0x03
) -> List[ECUInfo]:
    """
    Discover ECUs on the DoIP network using hybrid discovery.
    
    This function performs ISO 13400-2 compliant hybrid discovery:
    1. Broadcasts a Vehicle Identification Request to actively trigger responses
    2. Listens for Vehicle Announcement messages for the entire timeout period
    
    This approach finds both ECUs that respond to requests and those that send
    spontaneous announcements (e.g., newly connected devices).
    
    Args:
        interface: Network interface to use (None for default)
        timeout: Discovery timeout in seconds (time to listen for announcements)
        protocol_version: DoIP protocol version (default: 0x03)
        
    Returns:
        List of discovered ECU information (duplicates filtered by IP and logical address)
        
    Raises:
        DiscoveryError: If discovery fails due to network or protocol errors
        
    Example:
        >>> ecus = discover_ecus(timeout=5.0)
        >>> for ecu in ecus:
        ...     print(f"Found: {ecu}")
        >>> 
        >>> # Connect to first discovered ECU
        >>> if ecus:
        ...     client = ecus[0].connect()
    """
    try:
        discovered_ecus = []
        seen_ecus = set()  # To store (ip, logical_address) to avoid duplicates
        
        # Step 1: Broadcast Vehicle Identification Request
        # This triggers all online ECUs to respond with Vehicle Announcement messages
        try:
            DoIPClient.request_vehicle_identification(
                interface=interface,
                protocol_version=protocol_version
            )
        except Exception as e:
            # If broadcast fails, we can still listen for spontaneous announcements
            warnings.warn(f"Failed to broadcast vehicle identification request: {e}", RuntimeWarning)
        
        # Step 2: Listen for Vehicle Announcement messages for the full timeout period
        start_time = time.time()
        while time.time() - start_time < timeout:
            try:
                remaining_timeout = timeout - (time.time() - start_time)
                if remaining_timeout <= 0:
                    break

                # Listen for announcements with a short internal timeout
                # This allows the loop to check remaining_timeout frequently
                address, announcement = DoIPClient.await_vehicle_announcement(
                    timeout=min(remaining_timeout, 1.0),
                    interface=interface
                )
                
                ip, _ = address
                logical_address = announcement.logical_address
                
                # Avoid duplicate ECUs (same IP and logical address)
                if (ip, logical_address) not in seen_ecus:
                    ecu_info = ECUInfo(
                        ip=ip,
                        logical_address=logical_address,
                        eid=announcement.eid,
                        gid=announcement.gid,
                        further_action_required=announcement.further_action_required.value
                    )
                    discovered_ecus.append(ecu_info)
                    seen_ecus.add((ip, logical_address))

            except TimeoutError:
                # No announcement received within the internal timeout window
                # Continue listening until the full timeout period expires
                continue
        
        return discovered_ecus
        
    except exceptions.DiscoveryError:
        raise
    except Exception as e:
        raise exceptions.DiscoveryError(f"ECU discovery failed: {e}")


def get_entity(
    ip: str,
    timeout: float = 2.0,
    protocol_version: int = 0x03
) -> Optional[ECUInfo]:
    """
    Get entity information from a specific DoIP gateway/ECU.
    
    Args:
        ip: IP address of the DoIP entity
        timeout: Request timeout in seconds
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
            ip=ip,
            timeout=timeout,
            protocol_version=protocol_version
        )
        
        ip_address, _ = address
        
        return ECUInfo(
            ip=ip_address,
            logical_address=announcement.logical_address,
            eid=announcement.eid,
            gid=announcement.gid,
            further_action_required=announcement.further_action_required.value
        )
    except TimeoutError:
        return None
    except Exception as e:
        raise exceptions.DiscoveryError(f"Failed to get entity info from {ip}: {e}")


