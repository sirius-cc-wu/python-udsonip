# python-udsonip - Architecture & Roadmap

This document provides an overview of the project's current implementation status, architecture, and future roadmap.

**For usage instructions, see [README.md](README.md).**  
**For contribution guidelines, see [CONTRIBUTING.md](CONTRIBUTING.md).**

---

## ✅ Implementation Status

### Core Components

| Component | Status | Description |
|-----------|--------|-------------|
| `connection.py` | ✅ Complete | Enhanced DoIP connection with dynamic addressing |
| `client.py` | ✅ Complete | Unified UDS-on-IP client |
| `multi_ecu.py` | ✅ Complete | Multi-ECU manager with context switching |
| `discovery.py` | ✅ Complete | ECU discovery utilities (ISO 13400-2 compliant) |
| `exceptions.py` | ✅ Complete | Custom exception hierarchy |

### Implemented Features

1. ✅ **Single ECU Communication** - Direct connection and diagnostics
2. ✅ **Dynamic Target Switching** - Runtime address changes
3. ✅ **Multi-ECU Manager** - Context-based ECU switching
4. ✅ **UDS Service Wrappers** - Simplified common services
5. ✅ **Connection Management** - Proper resource handling
6. ✅ **Auto-Discovery** - Automatic ECU enumeration (broadcast + announcements)

### Examples

- ✅ `01_basic_single_ecu.py` - Single ECU communication
- ✅ `02_multi_ecu.py` - Multi-ECU example
- ✅ `03_dynamic_switching.py` - Address switching demo
- ✅ `04_discovery.py` - Discovery example

---

## 📋 Roadmap

### Phase 1: Stability & Testing (Current)

**High Priority:**
1. **Integration Testing** - Requires ECU simulator or real hardware
2. **API Documentation** - Sphinx-based reference
3. **Improve Test Coverage** - Target >85% coverage

### Phase 2: Enhanced Features

**Medium Priority:**
1. **Session Management** - Per-ECU session tracking and persistence
2. **Enhanced Error Handling** - Retry logic, better error messages
3. **Keep-Alive Support** - Automatic tester present per ECU
4. **Connection Pooling** - Efficient multi-ECU resource management

### Phase 3: Advanced Features

**Low Priority:**
1. **Utility Functions** - VIN decoder, DTC parser, common DIDs
2. **Async/Await Support** - asyncio integration for concurrent operations
3. **Config File Support** - YAML/JSON configuration files
4. **Enhanced Logging** - Structured logging with different levels
5. **Performance Metrics** - Timing and statistics
6. **Protocol Validation** - Strict ISO compliance checks

### Phase 4: Ecosystem

1. **Flash/Bootloader Utilities** - Firmware update helpers
2. **ODX Integration** - ODX file support for diagnostics
3. **GUI Tool** - Simple diagnostic GUI application
4. **Plugin System** - Extensibility for custom protocols

---

## 📊 Test Coverage Status

| Component | Implementation | Test Coverage | Priority |
|-----------|----------------|---------------|----------|
| UdsOnIpConnection | ✅ Complete | ~80% | Expand edge cases |
| UdsOnIpClient | ✅ Complete | ~70% | Add integration tests |
| DoIPMultiECUClient | ✅ Complete | ~60% | Add concurrency tests |
| Discovery | ✅ Complete | ~50% | Add mock-based tests |
| Exceptions | ✅ Complete | 100% | - |
| **Overall** | **✅ Complete** | **~65%** | **Target: 85%** |

---

## 🎯 Design Philosophy

### Key Principles

1. **Simplicity First**
   - Reduce boilerplate code by 90%
   - Sensible defaults for common use cases
   - Clear, intuitive API

2. **Flexibility**
   - Dynamic addressing via property: `client.target_address = 0x00E1`
   - Support both single and multi-ECU scenarios
   - Compatible with existing python-doipclient and python-udsoncan code

3. **Safety**
   - Context managers for resource management
   - Proper error handling and custom exceptions
   - Connection state tracking

4. **Standards Compliance**
   - ISO 13400 (DoIP) compliant
   - ISO 14229 (UDS) compliant
   - Hybrid discovery (request + announcement)

### Architecture Choices

**Composition over Inheritance:**
- Wraps `DoIPClient` and `udsoncan.Client`
- Doesn't force inheritance chains
- Easier to maintain and extend

**Context Managers:**
```python
with manager.ecu('engine') as ecu:
    # Automatic setup and cleanup
    # Exception-safe resource handling
```

**Dynamic Addressing:**
```python
client.target_address = 0x00E1  # Switch targets at runtime
```

---

## 🏗️ Architecture Overview

### Layer Structure

```
┌─────────────────────────────────────┐
│         Your Application            │  ← Simple, intuitive API
└────────────┬────────────────────────┘
             │
┌────────────▼────────────────────────┐
│         udsonip Layer               │  ← High-level abstractions
│  ┌──────────────┐  ┌──────────────┐│
│  │ UdsOnIpClient│  │ MultiECU Mgr ││  ← Client & Manager
│  └──────┬───────┘  └──────┬───────┘│
│         │                  │        │
│  ┌──────▼──────────────────▼──────┐│
│  │    UdsOnIpConnection          ││  ← Enhanced connector
│  │  (Dynamic addressing support)  ││
│  └──────┬────────────────────────┘│
└─────────┼──────────────────────────┘
          │
┌─────────▼──────────┐  ┌─────────────┐
│  python-udsoncan   │  │doipclient   │  ← Foundation libraries
│  (UDS Protocol)    │  │(DoIP Trans) │
└────────────────────┘  └─────────────┘
```

### Component Relationships

- **UdsOnIpConnection:** Bridge between DoIP transport and UDS protocol
- **UdsOnIpClient:** Main user-facing client for single ECU
- **DoIPMultiECUClient:** Manager for multiple ECUs on same gateway
- **Discovery:** Network-level ECU enumeration utilities

### Data Flow

1. **User code** calls high-level API (e.g., `read_data_by_identifier()`)
2. **UdsOnIpClient** wraps request in UDS protocol
3. **UdsOnIpConnection** sends via DoIP transport
4. **DoIPClient** handles network communication
5. **Response** flows back through layers to user code

---

## 📦 Dependencies

| Package | Version | Purpose |
|---------|---------|---------|
| **python-doipclient** | >= 1.1.7 | DoIP transport layer (ISO 13400) |
| **python-udsoncan** | >= 1.21 | UDS protocol layer (ISO 14229) |
| **Python** | >= 3.7 | Runtime environment |

**Development Dependencies:**
- pytest >= 6.0
- pytest-cov
- black (code formatter)
- flake8 (linter)

---

## 📊 Project Metrics

### Code Statistics

- **Lines of Code:** ~1,500 (core library)
- **Test Lines:** ~800
- **Documentation:** 3 comprehensive guides
- **Examples:** 4 working examples

### Complexity Reduction

| Metric | Raw Libraries | udsonip | Improvement |
|--------|--------------|---------|-------------|
| **Lines for basic read** | 20+ lines | 2 lines | 90% reduction |
| **Setup complexity** | High (custom class) | Low (one line) | Much simpler |
| **Multi-ECU support** | Manual | Built-in | Native support |

---

## 🎓 Learning Resources

### Standards
- **ISO 13400:** Road vehicles — Diagnostic communication over Internet Protocol (DoIP)
- **ISO 14229:** Road vehicles — Unified diagnostic services (UDS)

### Related Libraries
- **python-doipclient:** https://github.com/jacobschaer/python-doipclient
- **python-udsoncan:** https://github.com/pylessard/python-udsoncan

### Documentation
- **API Reference:** Coming soon (Sphinx)
- **Examples:** See `examples/` directory
- **Tutorials:** README.md and DEVELOPMENT.md

---

## 📄 License

MIT License - See [LICENSE](LICENSE) file for details.

Built with ❤️ on top of python-doipclient and python-udsoncan.