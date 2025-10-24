"""
udsonip - Enhanced UDS-on-IP Integration Library

Provides seamless integration between python-doipclient and python-udsoncan
with multi-ECU support, dynamic address switching, and enhanced features.
"""

__version__ = "0.1.0"
__author__ = "Sirius Wu"
__license__ = "MIT"

from .connection import UdsOnIpConnection
from .client import UdsOnIpClient
from .multi_ecu import DoIPMultiECUClient
from .discovery import discover_ecus, ECUInfo
from .exceptions import (
    UDSonIPException,
    ConnectionError,
    AddressSwitchError,
    DiscoveryError,
)

__all__ = [
    # Core classes
    "UdsOnIpConnection",
    "UdsOnIpClient",
    "DoIPMultiECUClient",
    # Discovery
    "discover_ecus",
    "ECUInfo",
    # Exceptions
    "UDSonIPException",
    "ConnectionError",
    "AddressSwitchError",
    "DiscoveryError",
]
