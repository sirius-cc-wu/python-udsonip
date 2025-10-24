"""
ECU discovery utilities for DoIP networks.
"""

from typing import List, Optional
from dataclasses import dataclass
import time
import ipaddress
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
    further_action: Optional[int] = None
    
    def __str__(self):
        return f"ECU({self.ip} @ {self.logical_address:#x})"
    
    def __repr__(self):
        return f"ECUInfo(ip='{self.ip}', logical_address={self.logical_address:#x})"
    
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
    Discover ECUs on the DoIP network using vehicle announcement.
    
    This function sends a vehicle identification request and waits for
    vehicle announcement messages from DoIP entities on the network.
    
    Args:
        interface: Network interface to use (None for default)
        timeout: Discovery timeout in seconds
        protocol_version: DoIP protocol version (default: 0x03)
        
    Returns:
        List of discovered ECU information
        
    Raises:
        DiscoveryError: If discovery fails
        
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
        
        start_time = time.time()
        while time.time() - start_time < timeout:
            try:
                # Use a short internal timeout to allow collecting multiple announcements
                remaining_timeout = timeout - (time.time() - start_time)
                if remaining_timeout <= 0:
                    break

                address, announcement = DoIPClient.await_vehicle_announcement(
                    timeout=min(remaining_timeout, 1.0), # Wait for max 1 second or remaining timeout
                    interface=interface
                )
                
                ip, _ = address
                logical_address = announcement.logical_address
                
                if (ip, logical_address) not in seen_ecus:
                    ecu_info = ECUInfo(
                        ip=ip,
                        logical_address=logical_address,
                        eid=announcement.eid,
                        gid=announcement.gid,
                        further_action=announcement.further_action_code
                    )
                    discovered_ecus.append(ecu_info)
                    seen_ecus.add((ip, logical_address))

            except TimeoutError:
                # No announcement received within the internal timeout, continue loop
                pass
            except Exception as e:
                # Log other errors but continue discovery
                # For now, re-raise as per existing structure
                raise exceptions.DiscoveryError(f"Error during ECU announcement: {e}")
        
        return discovered_ecus
        
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
            further_action=announcement.further_action_code
        )
    except TimeoutError:
        return None
    except Exception as e:
        raise exceptions.DiscoveryError(f"Failed to get entity info from {ip}: {e}")


def scan_network(
    network: str = "192.168.1.0/24",
    port: int = 13400,
    timeout: float = 1.0
) -> List[ECUInfo]:
    """
    Scan a network range for DoIP entities.
    
    Args:
        network: Network in CIDR notation (e.g., "192.168.1.0/24")
        port: DoIP port (default: 13400)
        timeout: Timeout per host in seconds
        
    Returns:
        List of discovered ECUs
        
    Example:
        >>> ecus = scan_network("192.168.1.0/24")
        >>> print(f"Found {len(ecus)} ECUs")
    """
    try:
        discovered_ecus = []
        
        # Parse CIDR notation
        network_obj = ipaddress.ip_network(network, strict=False)
        
        for ip_addr in network_obj.hosts():
            # Try to get entity information for each IP
            ecu = get_entity(str(ip_addr), timeout=timeout, protocol_version=0x03) # Default to 0x03
            if ecu:
                discovered_ecus.append(ecu)
        
        return discovered_ecus
    except Exception as e:
        raise exceptions.DiscoveryError(f"Network scan failed: {e}")