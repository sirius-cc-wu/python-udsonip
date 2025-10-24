# Contributing to python-udsonip

This guide is for developers who want to contribute to the python-udsonip library.

**For library users, see [README.md](README.md) instead.**  
**For project architecture, see [ARCHITECTURE.md](ARCHITECTURE.md).**

---

## Table of Contents

1. [Getting Started](#getting-started)
2. [Project Structure](#project-structure)
3. [Development Workflow](#development-workflow)
4. [Testing](#testing)
5. [Code Style](#code-style)
6. [Pull Request Process](#pull-request-process)
7. [Architecture Notes](#architecture-notes)

---

## Getting Started

### Prerequisites

- Python >= 3.7
- Git
- Basic understanding of UDS and DoIP protocols

### Development Setup

```
python-udsonip/
├── udsonip/              # Main package
│   ├── __init__.py       # Package exports
│   ├── connection.py     # Enhanced DoIP connection
│   ├── client.py         # Unified UDS-on-IP client
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

```bash
# Clone the repository
git clone https://github.com/sirius-cc-wu/python-udsonip.git
cd python-udsonip

# Create virtual environment (recommended)
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install in editable mode with dev dependencies
pip install -e ".[dev]"

# Or install dependencies manually
pip install doipclient udsoncan pytest pytest-cov black flake8
```

## Project Structure

---

## Development Workflow

### 1. Create a Feature Branch

```bash
git checkout -b feature/your-feature-name
# or
git checkout -b fix/your-bug-fix
```

### 2. Make Your Changes

- Write clean, readable code
- Add tests for new features
- Update documentation as needed
- Follow the code style guidelines (see below)

### 3. Run Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=udsonip --cov-report=html

# Run specific test file
pytest tests/test_connection.py -v

# Run specific test
pytest tests/test_connection.py::test_function_name -v
```

### 4. Format and Lint

```bash
# Format code
black udsonip/ tests/

# Lint
flake8 udsonip/ tests/
```

### 5. Commit Your Changes

```bash
git add .
git commit -m "feat: add feature description"
# or
git commit -m "fix: fix bug description"
```

**Commit Message Format:**
- `feat:` New feature
- `fix:` Bug fix
- `docs:` Documentation changes
- `test:` Test additions or changes
- `refactor:` Code refactoring
- `chore:` Maintenance tasks

### 6. Push and Create Pull Request

```bash
git push origin feature/your-feature-name
```

Then create a Pull Request on GitHub.

---

## Testing

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage report
pytest --cov=udsonip --cov-report=html

# Run specific test file
pytest tests/test_connection.py

# Run with verbose output
pytest -v

# Run discovery tests
pytest tests/test_discovery.py -v
```

### Writing Tests

- Place tests in `tests/` directory
- Name test files `test_*.py`
- Name test functions `test_*`
- Use descriptive test names
- Mock external dependencies (DoIPClient, etc.)
- Aim for >85% code coverage

Example test:

```python
import pytest
from udsonip import UdsOnIpClient

def test_client_initialization():
    """Test that client initializes with correct parameters."""
    client = UdsOnIpClient('192.168.1.10', 0x00E0)
    assert client.ecu_ip == '192.168.1.10'
    assert client.ecu_address == 0x00E0
```

---

## Code Style

### Python Style Guidelines

- **PEP 8 compliance** - Standard Python style guide
- **Line length:** 100 characters max
- **Type hints:** Use for all function parameters and returns
- **Docstrings:** Google style for all public APIs

### Formatting

Use **Black** for automatic code formatting:

```bash
black udsonip/ tests/
```

### Linting

Use **flake8** for linting:

```bash
flake8 udsonip/ tests/ --max-line-length=100
```

### Docstring Example

```python
def read_data_by_identifier(self, did: int) -> Response:
    """Read data from ECU by identifier.
    
    Args:
        did: Data identifier (DID) to read.
        
    Returns:
        UDS response object containing the data.
        
    Raises:
        NegativeResponseException: If ECU returns negative response.
        TimeoutException: If request times out.
    """
    pass
```

---

## Pull Request Process

### Before Submitting

- [ ] All tests pass (`pytest`)
- [ ] Code is formatted (`black`)
- [ ] Code is linted (`flake8`)
- [ ] Documentation is updated (if needed)
- [ ] Commit messages follow convention
- [ ] Branch is up to date with main

### PR Description Template

```markdown
## Description
Brief description of the changes

## Type of Change
- [ ] Bug fix
- [ ] New feature
- [ ] Breaking change
- [ ] Documentation update

## Testing
How has this been tested?

## Checklist
- [ ] Tests pass
- [ ] Code formatted with Black
- [ ] Documentation updated
```

### Review Process

1. Automated tests run on PR
2. Maintainer reviews code
3. Address review feedback
4. PR is merged when approved

---

## Architecture Notes

### Design Decisions

#### 1. Why separate UdsOnIpConnection class?

- Allows reuse of DoIPClient connection
- Supports dynamic address switching
- Clean separation of transport and protocol layers

#### 2. Why context managers for multi-ECU?

- Ensures proper resource cleanup
- Clear ECU switching semantics
- Better error handling per ECU

#### 3. Why wrapper around UDS Client?

- Simplified API for common operations
- Integration with DoIP features
- Consistent error handling across library

### Integration Points

#### With python-doipclient

The library primarily uses:
- `DoIPClient` for transport layer
- `DoIPClient.send_diagnostic_to_address()` for dynamic addressing
- `DoIPClient.request_vehicle_identification()` for broadcast discovery
- `DoIPClient.await_vehicle_announcement()` for listening to announcements
- `DoIPClient.get_entity()` for querying specific IPs

#### With python-udsoncan

The library integrates:
- `BaseConnection` interface implementation
- `Client` for UDS services
- Service classes for request/response handling

---

## Development Priorities

### Current Focus

See [ARCHITECTURE.md](ARCHITECTURE.md) for current implementation status and roadmap.

---

## Questions & Support

- **Issues:** https://github.com/sirius-cc-wu/python-udsonip/issues
- **Discussions:** GitHub Discussions (for questions and ideas)

---

## Release Process

**For maintainers only:**

1. Update version in `pyproject.toml`
2. Update `CHANGELOG.md`
3. Run full test suite
4. Create git tag: `git tag v1.0.0`
5. Push tag: `git push origin v1.0.0`
6. Build package: `python -m build`
7. Upload to PyPI: `twine upload dist/*`

---

Thank you for contributing to python-udsonip! 🚀