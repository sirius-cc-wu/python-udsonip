"""
udsonip - Enhanced UDS-on-IP Integration Library

Provides seamless integration between python-doipclient and python-udsoncan
with multi-ECU support, dynamic address switching, and enhanced features.
"""

__version__ = "0.2.0"
__author__ = "Sirius Wu"
__license__ = "MIT"

from .connection import UdsOnIpConnection
from .client import UdsOnIpClient
from .manager import DoIPManager
from .discovery import discover_ecus, get_entity
from .exceptions import (
    ConnectionError,
    AddressSwitchError,
    DiscoveryError,
    SessionError,
    ECUNotFoundError,
)

__all__ = [
    "UdsOnIpClient",
    "DoIPManager",
    "discover_ecus",
    "get_entity",
    "ConnectionError",
    "AddressSwitchError",
    "DiscoveryError",
    "SessionError",
    "ECUNotFoundError",
]
