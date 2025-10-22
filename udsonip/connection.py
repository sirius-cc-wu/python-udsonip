"""
Enhanced DoIP connection for UDS communication with dynamic target address support.
"""

from typing import Optional
from udsoncan.connections import BaseConnection
from doipclient import DoIPClient


class DoIPUDSConnection(BaseConnection):
    """
    Enhanced DoIP connection that supports dynamic target address switching.
    
    This connection class wraps a DoIPClient and provides the interface required
    by python-udsoncan while adding the ability to change the target ECU address
    at runtime without recreating the connection.
    
    Args:
        doip_client: DoIPClient instance to use for communication
        target_address: Optional target logical address. If not provided, uses
                       the address from doip_client
    
    Example:
        >>> from doipclient import DoIPClient
        >>> doip = DoIPClient('192.168.1.10', 0x00E0)
        >>> conn = DoIPUDSConnection(doip)
        >>> # Switch target address dynamically
        >>> conn.target_address = 0x00E1
    """
    
    def __init__(self, doip_client: DoIPClient, target_address: Optional[int] = None):
        BaseConnection.__init__(self, name='DoIPUDS')
        self._doip = doip_client
        self._target_address = target_address or doip_client._ecu_logical_address
        self._opened = False
    
    @property
    def target_address(self) -> int:
        """Get the current target logical address."""
        return self._target_address
    
    @target_address.setter
    def target_address(self, value: int):
        """
        Set a new target logical address for subsequent communications.
        
        Args:
            value: New target logical address (e.g., 0x00E0, 0x00E1)
        """
        self._target_address = value
        self.logger.info(f"Target address switched to {value:#x}")
    
    def open(self):
        """Open the DoIP connection."""
        if not self._opened:
            # DoIPClient connection is typically already established
            # We just mark as opened
            self._opened = True
            self.logger.info("DoIPUDSConnection opened")
    
    def close(self):
        """Close the DoIP connection."""
        if self._opened:
            self._opened = False
            self.logger.info("DoIPUDSConnection closed")
    
    def specific_send(self, payload: bytes):
        """
        Send a UDS payload to the current target address.
        
        Args:
            payload: UDS message payload to send
        """
        self.logger.debug(f"Sending {len(payload)} bytes to {self._target_address:#x}: {payload.hex()}")
        
        # Use send_diagnostic_to_address for dynamic addressing
        self._doip.send_diagnostic_to_address(
            self._target_address,
            bytearray(payload)
        )
    
    def specific_wait_frame(self, timeout: Optional[float] = None) -> Optional[bytes]:
        """
        Wait for and receive a UDS response frame.
        
        Args:
            timeout: Maximum time to wait for response in seconds
            
        Returns:
            Received frame data or None if timeout
        """
        try:
            # Receive diagnostic message
            response = self._doip.receive_diagnostic(timeout=timeout)
            if response:
                self.logger.debug(f"Received {len(response)} bytes: {response.hex()}")
                return bytes(response)
            return None
        except Exception as e:
            self.logger.error(f"Error receiving frame: {e}")
            raise
    
    def empty_rxbuffer(self):
        """Empty the reception buffer."""
        # DoIPClient handles buffering internally
        pass
    
    def is_open(self) -> bool:
        """Check if connection is open."""
        return self._opened
