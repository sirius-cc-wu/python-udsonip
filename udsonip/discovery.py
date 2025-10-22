"""
ECU discovery utilities for DoIP networks.
"""

from typing import List, Optional
from dataclasses import dataclass
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
        Create a DoIPUDSClient connected to this ECU.
        
        Args:
            client_ip: Optional client IP address
            **kwargs: Additional arguments for DoIPUDSClient
            
        Returns:
            DoIPUDSClient instance
        """
        from .client import DoIPUDSClient
        return DoIPUDSClient(
            ecu_ip=self.ip,
            ecu_address=self.logical_address,
            client_ip=client_ip,
            **kwargs
        )


def discover_ecus(
    interface: Optional[str] = None,
    timeout: float = 5.0,
    protocol_version: int = 0x02
) -> List[ECUInfo]:
    """
    Discover ECUs on the DoIP network using vehicle announcement.
    
    This function sends a vehicle identification request and waits for
    vehicle announcement messages from DoIP entities on the network.
    
    Args:
        interface: Network interface to use (None for default)
        timeout: Discovery timeout in seconds
        protocol_version: DoIP protocol version (default: 0x02)
        
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
        # Use DoIPClient's discovery mechanism
        # This is a simplified version - actual implementation would use
        # DoIPClient.await_vehicle_announcement() and parse responses
        
        discovered_ecus = []
        
        # TODO: Implement actual discovery using DoIPClient
        # For now, this is a placeholder showing the intended interface
        
        # Example of what the implementation would do:
        # 1. Send vehicle identification request broadcast
        # 2. Wait for vehicle announcement messages
        # 3. Parse announcements to extract ECU info
        # 4. Return list of ECUInfo objects
        
        return discovered_ecus
        
    except Exception as e:
        raise exceptions.DiscoveryError(f"ECU discovery failed: {e}")


def get_entity(
    ip: str,
    timeout: float = 2.0,
    protocol_version: int = 0x02
) -> Optional[ECUInfo]:
    """
    Get entity information from a specific DoIP gateway/ECU.
    
    Args:
        ip: IP address of the DoIP entity
        timeout: Request timeout in seconds
        protocol_version: DoIP protocol version
        
    Returns:
        ECUInfo if successful, None otherwise
        
    Example:
        >>> ecu = get_entity('192.168.1.10')
        >>> if ecu:
        ...     print(f"ECU at {ecu.ip}: {ecu.logical_address:#x}")
    """
    try:
        # TODO: Implement entity information request
        # Use DoIPClient.get_entity() or similar
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
        # TODO: Implement network scanning
        # 1. Parse CIDR notation
        # 2. Iterate through IP addresses
        # 3. Try to connect to each on DoIP port
        # 4. Get entity information
        # 5. Return list of discovered ECUs
        
        return []
    except Exception as e:
        raise exceptions.DiscoveryError(f"Network scan failed: {e}")
