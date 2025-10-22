"""
udsonip - Enhanced DoIP-UDS Integration Library

Provides seamless integration between python-doipclient and python-udsoncan
with multi-ECU support, dynamic address switching, and enhanced features.
"""

__version__ = "0.1.0"
__author__ = "Your Name"
__license__ = "MIT"

from .connection import DoIPUDSConnection
from .client import DoIPUDSClient
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
    "DoIPUDSConnection",
    "DoIPUDSClient",
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
