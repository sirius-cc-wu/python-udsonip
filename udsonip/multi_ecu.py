"""
Multi-ECU manager for handling multiple ECUs over a single DoIP connection.
"""

from typing import Dict, Optional
from contextlib import contextmanager
from doipclient import DoIPClient
from udsoncan.client import Client as UDSClient
from .connection import DoIPUDSConnection
from . import exceptions


class DoIPMultiECUClient:
    """
    Manager for communicating with multiple ECUs over a single DoIP gateway.
    
    This class maintains a single DoIP connection and allows switching between
    different ECU logical addresses using context managers for clean and safe
    multi-ECU communication.
    
    Args:
        gateway_ip: IP address of the DoIP gateway
        client_ip: Optional source IP address
        client_logical_address: Client logical address (default: 0x0E00)
        **kwargs: Additional arguments for DoIP connection
    
    Example:
        >>> manager = DoIPMultiECUClient('192.168.1.10')
        >>> manager.add_ecu('engine', 0x00E0)
        >>> manager.add_ecu('transmission', 0x00E1)
        >>> 
        >>> with manager.ecu('engine') as ecu:
        ...     vin = ecu.read_data_by_identifier(0xF190)
        >>> 
        >>> with manager.ecu('transmission') as ecu:
        ...     status = ecu.read_data_by_identifier(0x1234)
    """
    
    def __init__(
        self,
        gateway_ip: str,
        client_ip: Optional[str] = None,
        client_logical_address: int = 0x0E00,
        **kwargs
    ):
        self._gateway_ip = gateway_ip
        self._client_ip = client_ip
        self._client_logical_address = client_logical_address
        self._kwargs = kwargs
        
        # ECU registry: name -> logical address
        self._ecus: Dict[str, int] = {}
        
        # Cached connections and clients per ECU
        self._connections: Dict[str, DoIPUDSConnection] = {}
        self._clients: Dict[str, UDSClient] = {}
        
        # Shared DoIP client (created on first use)
        self._doip: Optional[DoIPClient] = None
        self._connected = False
    
    def add_ecu(self, name: str, logical_address: int):
        """
        Register an ECU in the manager.
        
        Args:
            name: Friendly name for the ECU (e.g., 'engine', 'transmission')
            logical_address: ECU logical address
        
        Example:
            >>> manager.add_ecu('engine', 0x00E0)
            >>> manager.add_ecu('transmission', 0x00E1)
            >>> manager.add_ecu('gateway', 0x0001)
        """
        self._ecus[name] = logical_address
    
    def remove_ecu(self, name: str):
        """
        Remove an ECU from the registry.
        
        Args:
            name: ECU name to remove
        """
        if name in self._ecus:
            del self._ecus[name]
            # Clean up cached connection/client
            if name in self._connections:
                del self._connections[name]
            if name in self._clients:
                del self._clients[name]
    
    def list_ecus(self) -> Dict[str, int]:
        """
        Get a dictionary of all registered ECUs.
        
        Returns:
            Dictionary mapping ECU names to logical addresses
        """
        return self._ecus.copy()
    
    def _ensure_connected(self):
        """Ensure the DoIP connection is established."""
        if not self._connected:
            # Create DoIP client (use gateway address 0x0001 or first ECU)
            gateway_address = 0x0001
            
            self._doip = DoIPClient(
                ecu_ip_address=self._gateway_ip,
                ecu_logical_address=gateway_address,
                tcp_port=13400,
                udp_port=13400,
                client_ip_address=self._client_ip,
                client_logical_address=self._client_logical_address,
                **self._kwargs
            )
            
            try:
                self._doip.connect()
                self._connected = True
            except Exception as e:
                raise exceptions.ConnectionError(f"Failed to connect to gateway {self._gateway_ip}: {e}")
    
    def _get_client(self, name: str) -> UDSClient:
        """
        Get or create a UDS client for the specified ECU.
        
        Args:
            name: ECU name
            
        Returns:
            UDS client instance
        """
        if name not in self._ecus:
            raise exceptions.ECUNotFoundError(f"ECU '{name}' not found in registry")
        
        # Return cached client if available
        if name in self._clients:
            return self._clients[name]
        
        # Ensure connected
        self._ensure_connected()
        
        # Create connection and client
        logical_address = self._ecus[name]
        connection = DoIPUDSConnection(self._doip, logical_address)
        connection.open()
        
        client = UDSClient(connection)
        
        # Cache for reuse
        self._connections[name] = connection
        self._clients[name] = client
        
        return client
    
    @contextmanager
    def ecu(self, name: str):
        """
        Context manager for safe ECU communication.
        
        Args:
            name: Name of the ECU to communicate with
            
        Yields:
            UDS client configured for the specified ECU
        
        Example:
            >>> with manager.ecu('engine') as ecu:
            ...     vin = ecu.read_data_by_identifier(0xF190)
            ...     print(f"Engine VIN: {vin.data.decode()}")
        """
        client = self._get_client(name)
        try:
            yield client
        except Exception as e:
            # Re-raise with ECU context
            raise type(e)(f"Error communicating with ECU '{name}': {e}") from e
    
    def switch_to(self, name: str) -> UDSClient:
        """
        Switch to a different ECU (non-context-manager version).
        
        Args:
            name: ECU name to switch to
            
        Returns:
            UDS client for the ECU
            
        Note:
            Using the context manager (ecu()) is preferred for safety.
        """
        return self._get_client(name)
    
    def close(self):
        """Close all connections and clean up resources."""
        # Close all cached connections
        for connection in self._connections.values():
            try:
                connection.close()
            except:
                pass
        
        # Disconnect DoIP client
        if self._doip and self._connected:
            try:
                self._doip.disconnect()
            except:
                pass
            self._connected = False
        
        # Clear caches
        self._connections.clear()
        self._clients.clear()
    
    def __enter__(self):
        """Context manager entry."""
        self._ensure_connected()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.close()
    
    def __del__(self):
        """Cleanup on deletion."""
        self.close()
