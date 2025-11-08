# python-udsonip

**Enhanced UDS-on-IP Integration Library**

> **Note:** Install via `pip install udsonip` (package name without the `python-` prefix)

`udsonip` is a high-level Python library that seamlessly integrates [python-doipclient](https://github.com/jacobschaer/python-doipclient) and [python-udsoncan](https://github.com/pylessard/python-udsoncan) to provide enhanced multi-ECU support, improved ergonomics, and advanced features for automotive diagnostics over DoIP (Diagnostics over Internet Protocol).

---

**📖 Documentation:**
- **For Users:** This README (installation, usage, examples)
- **For Contributors:** See [CONTRIBUTING.md](CONTRIBUTING.md) (setup, testing, contribution guidelines)
- **Project Status:** See [DEVELOPMENT.md](DEVELOPMENT.md) (features, roadmap, architecture)

## Features

- 🎯 **Dynamic Target Address Support** - Runtime switching between ECU addresses
- 🔄 **Multi-ECU Management** - Single connection managing multiple ECUs with context managers
- 🔍 **Auto-Discovery** - Automatic ECU enumeration and discovery
- 📡 **Enhanced Session Management** - Per-ECU session tracking and persistence
- 🛠️ **Simplified API** - Less boilerplate, sensible defaults

## Installation

```bash
pip install udsonip
```

## Quick Start

### Single ECU Communication

```python
from udsonip import UdsOnIpClient

# Simple single-ECU client
client = UdsOnIpClient('192.168.1.10', 0x00E0)
response = client.read_data_by_identifier(0xF190)  # Read VIN
print(f"VIN: {response.data.decode()}")
client.close()
```

### Multi-ECU Communication

```python
from udsonip import DoIPManager

# Multi-ECU manager
manager = DoIPManager('192.168.1.10')
manager.add_ecu('engine', 0x00E0)
manager.add_ecu('transmission', 0x00E1)

# Switch between ECUs seamlessly
with manager.ecu('engine') as ecu:
    vin = ecu.read_data_by_identifier(0xF190)

with manager.ecu('transmission') as ecu:
    status = ecu.read_data_by_identifier(0x1234)
```

### Auto-Discovery

```python
from udsonip import discover_ecus

# Discover all ECUs on the network
ecus = discover_ecus(timeout=5.0)
for ecu in ecus:
    print(f"Found ECU: {ecu.ip} @ {ecu.logical_address:#x}")
    
# Connect to discovered ECU
client = ecus[0].connect()
```

### Advanced Usage - Dynamic Target Switching

```python
from udsonip import UdsOnIpClient

client = UdsOnIpClient(
    ecu_ip='192.168.1.10',
    ecu_address=0x00E0,
    auto_reconnect=True,
    keep_alive=True,
)

# Dynamic target address switching
client.target_address = 0x00E1
response = client.tester_present()

client.target_address = 0x00E2
response = client.read_data_by_identifier(0xF190)
```

## Architecture

```
┌─────────────────────────────────────┐
│         Your Application            │
└────────────┬────────────────────────┘
             │
┌────────────▼────────────────────────┐
│         udsonip Layer               │
│  ┌──────────────┐  ┌──────────────┐│
│  │ UdsOnIpClient│  │ MultiECU Mgr ││
│  └──────┬───────┘  └──────┬───────┘│
│         │                  │        │
│  ┌──────▼──────────────────▼──────┐│
│  │    UdsOnIpConnection          ││
│  └──────┬────────────────────────┘│
└─────────┼──────────────────────────┘
          │
┌─────────▼──────────┐  ┌─────────────┐
│  python-udsoncan   │  │doipclient   │
│  (UDS Protocol)    │  │(DoIP Trans) │
└────────────────────┘  └─────────────┘
```

## Key Components

- **UdsOnIpConnection** - Enhanced connector with dynamic address support
- **UdsOnIpClient** - Unified client wrapping both libraries
- **DoIPManager** - Multi-ECU manager with context switching
- **discover_ecus()** - ECU discovery utilities

## Why udsonip?

### Before (using libraries separately):

```python
from doipclient import DoIPClient
from udsoncan.client import Client
from udsoncan.connections import BaseConnection

# Manual setup required - 20+ lines of boilerplate
doip_client = DoIPClient('192.168.1.10', 0x00E0)
doip_client.connect()

class DoIPConnection(BaseConnection):
    def __init__(self, doip_client):
        self._doip = doip_client
    
    def send(self, data):
        self._doip.send_diagnostic(data)
    
    def wait_frame(self, timeout=None):
        return self._doip.receive_diagnostic(timeout)

connection = DoIPConnection(doip_client)
uds_client = Client(connection)

# Finally use UDS client
response = uds_client.read_data_by_identifier(0xF190)
```

### After (using udsonip):

```python
from udsonip import UdsOnIpClient

# Just 2 lines!
client = UdsOnIpClient('192.168.1.10', 0x00E0)
response = client.read_data_by_identifier(0xF190)
```

**Result: 90% less code, 100% more readable!** 🎉

## Requirements

- Python >= 3.7
- python-doipclient >= 1.1.7
- python-udsoncan >= 1.21

## API Reference

### UdsOnIpClient

Main client for single ECU communication.

```python
client = UdsOnIpClient(
    ecu_ip='192.168.1.10',
    ecu_address=0x00E0,
    client_ip=None,           # Auto-detect
    auto_reconnect=False,
    keep_alive=False,
)
```

**Key Methods:**
- `read_data_by_identifier(did)` - Read data by identifier
- `write_data_by_identifier(did, data)` - Write data
- `tester_present()` - Send tester present
- `diagnostic_session_control(session)` - Change diagnostic session
- `ecu_reset(reset_type)` - Reset ECU
- `close()` - Close connection

### DoIPManager

Manager for multiple ECUs on the same gateway.

```python
manager = DoIPManager('192.168.1.10')
manager.add_ecu('engine', 0x00E0)
manager.add_ecu('transmission', 0x00E1)

with manager.ecu('engine') as ecu:
    # Use ecu like UdsOnIpClient
    vin = ecu.read_data_by_identifier(0xF190)
```

### Discovery Functions

```python
from udsonip import discover_ecus, ECUInfo

# Discover all ECUs
ecus = discover_ecus(interface=None, timeout=5.0)

# Connect to discovered ECU
client = ecus[0].connect()
```

## Learning Resources

- **DoIP Standard:** ISO 13400 (Diagnostics over Internet Protocol)
- **UDS Standard:** ISO 14229 (Unified Diagnostic Services)
- **python-doipclient:** https://github.com/jacobschaer/python-doipclient
- **python-udsoncan:** https://github.com/pylessard/python-udsoncan

## Contributing

Contributions are welcome! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for:
- Development environment setup
- Running tests
- Code style guidelines
- Contribution workflow

## License

MIT License - see [LICENSE](LICENSE) file for details.

## Support & Community

- **Issues:** https://github.com/sirius-cc-wu/python-udsonip/issues
- **Documentation:** https://python-udsonip.readthedocs.io
- **Examples:** See `examples/` directory in the repository

## Acknowledgments

Built on top of:
- [python-doipclient](https://github.com/jacobschaer/python-doipclient) by Jacob Schaer
- [python-udsoncan](https://github.com/pylessard/python-udsoncan) by Pier-Yves Lessard
