"""
Tests for udsonip exceptions.
"""

import pytest
from udsonip import exceptions


def test_base_exception():
    """Test base UDSonIPException."""
    exc = exceptions.UDSonIPException("test message")
    assert str(exc) == "test message"
    assert isinstance(exc, Exception)


def test_connection_error():
    """Test ConnectionError."""
    exc = exceptions.ConnectionError("connection failed")
    assert isinstance(exc, exceptions.UDSonIPException)
    assert str(exc) == "connection failed"


def test_address_switch_error():
    """Test AddressSwitchError."""
    exc = exceptions.AddressSwitchError("switch failed")
    assert isinstance(exc, exceptions.UDSonIPException)


def test_discovery_error():
    """Test DiscoveryError."""
    exc = exceptions.DiscoveryError("discovery failed")
    assert isinstance(exc, exceptions.UDSonIPException)


def test_session_error():
    """Test SessionError."""
    exc = exceptions.SessionError("session failed")
    assert isinstance(exc, exceptions.UDSonIPException)


def test_ecu_not_found_error():
    """Test ECUNotFoundError."""
    exc = exceptions.ECUNotFoundError("ECU not found")
    assert isinstance(exc, exceptions.UDSonIPException)
