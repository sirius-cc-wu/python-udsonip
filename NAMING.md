# Package Naming Convention

## Repository vs Package Name

Following the common Python convention used by our dependencies:

| Component | Name |
|-----------|------|
| **Repository** | `python-udsonip` |
| **PyPI Package** | `udsonip` |
| **Import Name** | `udsonip` |

## Why This Convention?

### Repository Name: `python-udsonip`
- Clearly indicates it's a Python package
- Matches dependencies: `python-doipclient`, `python-udsoncan`
- Distinguishes from potential implementations in other languages
- Common on GitHub/GitLab

### Package Name: `udsonip`
- Short and easy to type: `pip install udsonip`
- Clean import: `from udsonip import DoIPUDSClient`
- Follows modern Python convention (like `requests`, `flask`)
- The `python-` prefix is redundant on PyPI (all packages are Python)

## Comparison with Dependencies

```
Repository          PyPI Package       Import
==========          ============       ======
python-doipclient → doipclient      → from doipclient import DoIPClient
python-udsoncan   → udsoncan        → from udsoncan import Client
python-udsonip    → udsonip         → from udsonip import DoIPUDSClient
```

## Installation & Usage

```bash
# Clone repository
git clone https://github.com/sirius-cc-wu/python-udsonip.git
cd python-udsonip

# Install package
pip install udsonip

# Or install from source
pip install -e .
```

```python
# Use in code
from udsonip import DoIPUDSClient

client = DoIPUDSClient('192.168.1.10', 0x00E0)
```

## Historical Context

The `python-` prefix convention comes from:

1. **System Package Managers**: Debian/Ubuntu use `python-*` for Python packages
   ```bash
   apt install python-requests  # System package
   pip install requests         # PyPI package
   ```

2. **Multi-Language Projects**: When a project has implementations in multiple languages
   ```
   python-jenkins
   ruby-jenkins
   go-jenkins
   ```

3. **GitHub Organization**: Makes Python repos easily identifiable

On PyPI, the `python-` prefix is generally dropped because:
- All packages on PyPI are Python packages
- Shorter names are easier to type
- Modern convention favors simplicity
