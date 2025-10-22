# python-udsonip

**Enhanced DoIP-UDS Integration Library**

> **Note:** Install via `pip install udsonip` (package name without the `python-` prefix)

`udsonip` is a high-level Python library that seamlessly integrates [python-doipclient](https://github.com/jacobschaer/python-doipclient) and [python-udsoncan](https://github.com/pylessard/python-udsoncan) to provide enhanced multi-ECU support, improved ergonomics, and advanced features for automotive diagnostics over DoIP (Diagnostics over Internet Protocol).

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
from udsonip import DoIPUDSClient

# Simple single-ECU client
client = DoIPUDSClient('192.168.1.10', 0x00E0)
response = client.read_data_by_identifier(0xF190)  # Read VIN
print(f"VIN: {response.data.decode()}")
client.close()
```

### Multi-ECU Communication

```python
from udsonip import DoIPMultiECUClient

# Multi-ECU manager
manager = DoIPMultiECUClient('192.168.1.10')
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
from udsonip import DoIPUDSClient

client = DoIPUDSClient(
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
udsonip integrates:
  ┌─────────────────┐
  │  python-udsoncan│  (UDS protocol)
  └────────┬────────┘
           │
  ┌────────▼────────┐
  │    udsonip      │  (Enhanced integration layer)
  └────────┬────────┘
           │
  ┌────────▼────────┐
  │python-doipclient│  (DoIP transport)
  └─────────────────┘
```

## Key Components

- **DoIPUDSConnection** - Enhanced connector with dynamic address support
- **DoIPUDSClient** - Unified client wrapping both libraries
- **DoIPMultiECUClient** - Multi-ECU manager with context switching
- **discover_ecus()** - ECU discovery utilities

## Comparison with Plain Usage

### Before (using libraries separately):

```python
from doipclient import DoIPClient
from udsoncan.client import Client
from udsoncan.connections import BaseConnection

# Manual setup required
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

# Use UDS client
response = uds_client.read_data_by_identifier(0xF190)
```

### After (using udsonip):

```python
from udsonip import DoIPUDSClient

client = DoIPUDSClient('192.168.1.10', 0x00E0)
response = client.read_data_by_identifier(0xF190)
```

## Documentation

Full documentation available at: https://udsonip.readthedocs.io

## Requirements

- Python >= 3.7
- python-doipclient >= 1.1.7
- python-udsoncan >= 1.21

## Contributing

Contributions are welcome! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for details.

## License

MIT License - see [LICENSE](LICENSE) file for details.

## Acknowledgments

Built on top of:
- [python-doipclient](https://github.com/jacobschaer/python-doipclient) by Jacob Schaer
- [python-udsoncan](https://github.com/pylessard/python-udsoncan) by Pier-Yves Lessard

## Roadmap

- [ ] Async/await support
- [ ] DTC helpers
- [ ] Flash/bootloader utilities
- [ ] Configuration file support (YAML/JSON)
- [ ] Enhanced logging
- [ ] Protocol validation
- [ ] Performance metrics
