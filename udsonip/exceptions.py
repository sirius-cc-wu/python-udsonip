"""
Custom exceptions for udsonip library.
"""


class UDSonIPException(Exception):
    """Base exception for all udsonip errors."""
    pass


class ConnectionError(UDSonIPException):
    """Raised when connection to ECU fails."""
    pass


class AddressSwitchError(UDSonIPException):
    """Raised when switching target address fails."""
    pass


class DiscoveryError(UDSonIPException):
    """Raised when ECU discovery fails."""
    pass


class SessionError(UDSonIPException):
    """Raised when session management fails."""
    pass


class ECUNotFoundError(UDSonIPException):
    """Raised when requested ECU is not found in registry."""
    pass
