"""
Tests for udsonip connection module.
"""

import pytest
from unittest.mock import Mock, MagicMock
from udsonip.connection import DoIPUDSConnection


class TestDoIPUDSConnection:
    """Tests for DoIPUDSConnection class."""
    
    def test_init_with_explicit_address(self):
        """Test initialization with explicit target address."""
        mock_doip = Mock()
        mock_doip._ecu_logical_address = 0x00E0
        
        conn = DoIPUDSConnection(mock_doip, target_address=0x00E1)
        
        assert conn.target_address == 0x00E1
        assert conn._doip == mock_doip
    
    def test_init_with_default_address(self):
        """Test initialization using DoIPClient's address."""
        mock_doip = Mock()
        mock_doip._ecu_logical_address = 0x00E0
        
        conn = DoIPUDSConnection(mock_doip)
        
        assert conn.target_address == 0x00E0
    
    def test_target_address_setter(self):
        """Test changing target address."""
        mock_doip = Mock()
        mock_doip._ecu_logical_address = 0x00E0
        
        conn = DoIPUDSConnection(mock_doip)
        conn.target_address = 0x00E2
        
        assert conn.target_address == 0x00E2
    
    def test_open_close(self):
        """Test open and close operations."""
        mock_doip = Mock()
        mock_doip._ecu_logical_address = 0x00E0
        
        conn = DoIPUDSConnection(mock_doip)
        
        assert not conn.is_open()
        
        conn.open()
        assert conn.is_open()
        
        conn.close()
        assert not conn.is_open()
    
    def test_specific_send(self):
        """Test sending data."""
        mock_doip = Mock()
        mock_doip._ecu_logical_address = 0x00E0
        
        conn = DoIPUDSConnection(mock_doip, target_address=0x00E1)
        payload = b'\x10\x01'  # Diagnostic session control
        
        conn.specific_send(payload)
        
        mock_doip.send_diagnostic_to_address.assert_called_once_with(
            0x00E1,
            bytearray(payload)
        )
    
    def test_specific_wait_frame(self):
        """Test receiving data."""
        mock_doip = Mock()
        mock_doip._ecu_logical_address = 0x00E0
        mock_doip.receive_diagnostic.return_value = b'\x50\x01\x00\x00'
        
        conn = DoIPUDSConnection(mock_doip)
        
        response = conn.specific_wait_frame(timeout=1.0)
        
        assert response == b'\x50\x01\x00\x00'
        mock_doip.receive_diagnostic.assert_called_once_with(timeout=1.0)
    
    def test_specific_wait_frame_timeout(self):
        """Test receiving data with timeout."""
        mock_doip = Mock()
        mock_doip._ecu_logical_address = 0x00E0
        mock_doip.receive_diagnostic.return_value = None
        
        conn = DoIPUDSConnection(mock_doip)
        
        response = conn.specific_wait_frame(timeout=1.0)
        
        assert response is None
