"""
Tests for udsonip discovery module.
"""

import pytest
from udsonip.discovery import ECUInfo


class TestECUInfo:
    """Tests for ECUInfo dataclass."""
    
    def test_init(self):
        """Test ECUInfo initialization."""
        ecu = ECUInfo(
            ip='192.168.1.10',
            logical_address=0x00E0,
            eid=b'VIN12345678901234',
            gid=b'\x00\x01'
        )
        
        assert ecu.ip == '192.168.1.10'
        assert ecu.logical_address == 0x00E0
        assert ecu.eid == b'VIN12345678901234'
        assert ecu.gid == b'\x00\x01'
    
    def test_str(self):
        """Test string representation."""
        ecu = ECUInfo(ip='192.168.1.10', logical_address=0x00E0)
        assert str(ecu) == "ECU(192.168.1.10 @ 0xe0)"
    
    def test_repr(self):
        """Test repr representation."""
        ecu = ECUInfo(ip='192.168.1.10', logical_address=0x00E0)
        assert repr(ecu) == "ECUInfo(ip='192.168.1.10', logical_address=0xe0)"
