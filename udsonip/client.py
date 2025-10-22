"""
Enhanced DoIP-UDS client with simplified API.
"""

from typing import Optional, Union
from doipclient import DoIPClient
from udsoncan.client import Client as UDSClient
from udsoncan import services
from .connection import DoIPUDSConnection
from . import exceptions


class DoIPUDSClient:
    """
    Unified DoIP-UDS client providing simplified access to UDS services.
    
    This client wraps both DoIPClient and UDS Client, providing a single
    interface for automotive diagnostics over DoIP with support for dynamic
    target address switching.
    
    Args:
        ecu_ip: IP address of the DoIP gateway/ECU
        ecu_address: Logical address of the target ECU
        client_ip: Optional source IP address (auto-detected if None)
        client_logical_address: Optional client logical address (default: 0x0E00)
        activation_type: DoIP activation type (default: 0)
        protocol_version: DoIP protocol version (default: 0x02)
        auto_reconnect: Automatically reconnect on connection loss
        keep_alive: Send keep-alive messages
        **kwargs: Additional arguments passed to UDS Client
    
    Example:
        >>> client = DoIPUDSClient('192.168.1.10', 0x00E0)
        >>> response = client.read_data_by_identifier(0xF190)
        >>> print(f"VIN: {response.data.decode()}")
        >>> client.close()
    """
    
    def __init__(
        self,
        ecu_ip: str,
        ecu_address: int,
        client_ip: Optional[str] = None,
        client_logical_address: int = 0x0E00,
        activation_type: int = 0,
        protocol_version: int = 0x02,
        auto_reconnect: bool = False,
        keep_alive: bool = False,
        **kwargs
    ):
        # Create DoIP client
        self._doip = DoIPClient(
            ecu_ip_address=ecu_ip,
            ecu_logical_address=ecu_address,
            tcp_port=13400,
            udp_port=13400,
            client_ip_address=client_ip,
            client_logical_address=client_logical_address,
            activation_type=activation_type,
            protocol_version=protocol_version,
        )
        
        # Store configuration
        self._auto_reconnect = auto_reconnect
        self._keep_alive = keep_alive
        
        # Create enhanced connection
        self._connection = DoIPUDSConnection(self._doip, ecu_address)
        
        # Create UDS client
        self._uds = UDSClient(self._connection, **kwargs)
        
        # Connect
        try:
            self._doip.connect()
            self._connection.open()
        except Exception as e:
            raise exceptions.ConnectionError(f"Failed to connect to {ecu_ip}:{ecu_address:#x}: {e}")
    
    @property
    def target_address(self) -> int:
        """Get the current target ECU logical address."""
        return self._connection.target_address
    
    @target_address.setter
    def target_address(self, value: int):
        """
        Change the target ECU logical address.
        
        Args:
            value: New target logical address
        
        Example:
            >>> client.target_address = 0x00E1
            >>> response = client.tester_present()
        """
        try:
            self._connection.target_address = value
        except Exception as e:
            raise exceptions.AddressSwitchError(f"Failed to switch address to {value:#x}: {e}")
    
    @property
    def uds(self) -> UDSClient:
        """Access the underlying UDS client for advanced operations."""
        return self._uds
    
    def close(self):
        """Close the connection to the ECU."""
        try:
            self._connection.close()
            self._doip.disconnect()
        except Exception as e:
            raise exceptions.ConnectionError(f"Error closing connection: {e}")
    
    def __enter__(self):
        """Context manager entry."""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.close()
    
    # Convenience methods wrapping common UDS services
    
    def tester_present(self, suppress_response: bool = False):
        """
        Send TesterPresent service request.
        
        Args:
            suppress_response: If True, suppress positive response
            
        Returns:
            Service response
        """
        return self._uds.tester_present(suppress_response=suppress_response)
    
    def read_data_by_identifier(self, did: Union[int, list]):
        """
        Read data by identifier (service 0x22).
        
        Args:
            did: Data identifier or list of identifiers
            
        Returns:
            Service response with .data attribute
        """
        return self._uds.read_data_by_identifier(did)
    
    def write_data_by_identifier(self, did: int, data: bytes):
        """
        Write data by identifier (service 0x2E).
        
        Args:
            did: Data identifier
            data: Data to write
            
        Returns:
            Service response
        """
        return self._uds.write_data_by_identifier(did, data)
    
    def read_dtc_information(self, dtc_status_mask: int = 0xFF):
        """
        Read DTC information (service 0x19).
        
        Args:
            dtc_status_mask: DTC status mask
            
        Returns:
            Service response with DTC information
        """
        return self._uds.read_dtc_information(
            services.ReadDTCInformation.Subfunction.reportDTCByStatusMask,
            dtc_status_mask
        )
    
    def clear_dtc(self, group: int = 0xFFFFFF):
        """
        Clear diagnostic trouble codes (service 0x14).
        
        Args:
            group: DTC group to clear (default: all DTCs)
            
        Returns:
            Service response
        """
        return self._uds.clear_dtc(group)
    
    def ecu_reset(self, reset_type: int = 1):
        """
        Request ECU reset (service 0x11).
        
        Args:
            reset_type: Reset type (1=hard reset, 2=key off/on, 3=soft reset)
            
        Returns:
            Service response
        """
        return self._uds.ecu_reset(reset_type)
    
    def change_session(self, session: int):
        """
        Change diagnostic session (service 0x10).
        
        Args:
            session: Session type (1=default, 2=programming, 3=extended)
            
        Returns:
            Service response
        """
        return self._uds.change_session(session)
    
    def security_access(self, level: int, key: Optional[bytes] = None):
        """
        Request security access (service 0x27).
        
        Args:
            level: Security level
            key: Security key (None for seed request)
            
        Returns:
            Service response
        """
        if key is None:
            return self._uds.request_seed(level)
        else:
            return self._uds.send_key(level, key)
    
    def routine_control(self, routine_id: int, control_type: int = 1, data: Optional[bytes] = None):
        """
        Execute routine control (service 0x31).
        
        Args:
            routine_id: Routine identifier
            control_type: Control type (1=start, 2=stop, 3=request results)
            data: Optional routine data
            
        Returns:
            Service response
        """
        return self._uds.start_routine(routine_id, data) if control_type == 1 else \
               self._uds.stop_routine(routine_id, data) if control_type == 2 else \
               self._uds.get_routine_result(routine_id, data)
