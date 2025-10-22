# python-udsonip Development Guide

## Project Structure

```
python-udsonip/
├── udsonip/              # Main package
│   ├── __init__.py       # Package exports
│   ├── connection.py     # Enhanced DoIP connection
│   ├── client.py         # Unified DoIP-UDS client
│   ├── multi_ecu.py      # Multi-ECU manager
│   ├── discovery.py      # ECU discovery utilities
│   └── exceptions.py     # Custom exceptions
├── examples/             # Usage examples
├── tests/                # Unit tests
├── docs/                 # Documentation
├── pyproject.toml        # Project configuration
├── README.md             # Project readme
└── LICENSE               # MIT license
```

## Installation for Development

```bash
cd /home/ccwu/Projects/udsonip

# Install in editable mode with dev dependencies
pip install -e ".[dev]"

# Or install dependencies manually
pip install doipclient python-udsoncan pytest pytest-cov
```

## Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=udsonip --cov-report=html

# Run specific test file
pytest tests/test_connection.py
```

## Next Steps

### 1. Implement Discovery Functions (Priority: High)

The discovery module currently has placeholder implementations. Complete:

- `discover_ecus()` - Use DoIPClient's vehicle announcement
- `get_entity()` - Query specific entity information
- `scan_network()` - Network scanning functionality

Reference: python-doipclient documentation for vehicle announcement.

### 2. Add Session Management (Priority: Medium)

Create `session.py` module with:

- Session state tracking per ECU
- Automatic session restoration
- Session timeout handling

### 3. Enhance Multi-ECU Manager (Priority: Medium)

Add features to `multi_ecu.py`:

- Connection pooling
- Concurrent request handling (thread-safe)
- Keep-alive per ECU

### 4. Add Helper Utilities (Priority: Low)

Create `utils.py` with:

- VIN decoder
- DTC parser
- Data formatters
- Common DIDs constants

### 5. Improve Error Handling (Priority: Medium)

- Add retry logic for transient failures
- Better error messages with context
- Timeout management

### 6. Documentation (Priority: High)

Create in `docs/`:

- API reference (Sphinx)
- User guide
- Migration guide from raw doipclient/udsoncan
- Architecture overview

### 7. Testing (Priority: High)

Expand test coverage:

- Unit tests for all modules (target: >85%)
- Integration tests (requires ECU simulator)
- Mock-based testing for discovery
- End-to-end examples

### 8. Advanced Features (Priority: Low)

Future enhancements:

- Async/await support (asyncio)
- Configuration file support (YAML/JSON)
- Logging improvements
- Performance metrics
- Protocol validation

## Development Workflow

1. **Feature Branch**
   ```bash
   git checkout -b feature/discovery-implementation
   ```

2. **Make Changes**
   - Edit code
   - Add/update tests
   - Update documentation

3. **Test**
   ```bash
   pytest
   black udsonip/  # Format code
   flake8 udsonip/  # Lint
   ```

4. **Commit**
   ```bash
   git add .
   git commit -m "Implement ECU discovery functionality"
   ```

## Key Integration Points

### With python-doipclient

The library primarily uses:
- `DoIPClient` for transport
- `DoIPClient.send_diagnostic_to_address()` for dynamic addressing
- Vehicle announcement for discovery

### With python-udsoncan

The library integrates:
- `BaseConnection` interface
- `Client` for UDS services
- Service classes for request/response

## Example Usage

### Current Implementation

```python
from udsonip import DoIPUDSClient

# Single ECU (WORKS NOW)
client = DoIPUDSClient('192.168.1.10', 0x00E0)
response = client.read_data_by_identifier(0xF190)
client.close()

# Multi-ECU (WORKS NOW)
from udsonip import DoIPMultiECUClient

manager = DoIPMultiECUClient('192.168.1.10')
manager.add_ecu('engine', 0x00E0)
manager.add_ecu('transmission', 0x00E1)

with manager.ecu('engine') as ecu:
    vin = ecu.read_data_by_identifier(0xF190)

manager.close()
```

### To Be Implemented

```python
from udsonip import discover_ecus

# Discovery (TODO)
ecus = discover_ecus(timeout=5.0)
for ecu in ecus:
    print(f"Found: {ecu}")
```

## Code Style

- Follow PEP 8
- Use type hints
- Docstrings for all public APIs (Google style)
- Black for formatting (line length: 100)
- Tests for new features

## Release Checklist

- [ ] All tests passing
- [ ] Documentation updated
- [ ] CHANGELOG.md updated
- [ ] Version bumped in pyproject.toml
- [ ] Tagged release
- [ ] Built and uploaded to PyPI

## Questions?

The main design decisions:

1. **Why separate connection class?**
   - Allows reuse of DoIPClient connection
   - Supports dynamic address switching
   - Clean separation of transport and protocol

2. **Why context managers for multi-ECU?**
   - Ensures proper resource cleanup
   - Clear ECU switching semantics
   - Error handling per ECU

3. **Why wrapper around UDS Client?**
   - Simplified API for common operations
   - Integration with DoIP features
   - Consistent error handling

## Contact

- Issues: https://github.com/sirius-cc-wu/python-udsonip/issues
