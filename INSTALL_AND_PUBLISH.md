# FCube Installation & Publishing Guide

This guide covers installation, development setup, and publishing workflows for FCube CLI.

## Quick Installation

### For Users: Global Installation

Install fcube globally using one of these methods:

```bash
# Method 1: Install from GitHub (when published)
uv tool install git+https://github.com/amal-babu-git/fcube.git

# Method 2: Install from local clone
git clone https://github.com/amal-babu-git/fcube.git
cd fcube
uv tool install .

# Method 3: Install from PyPI (when published)
uv tool install fcube
```

Verify installation:
```bash
fcube --version
fcube --help
```

### For Developers: Local Development

```bash
# Clone the repository
git clone https://github.com/amal-babu-git/fcube.git
cd fcube

# Option 1: Use uv run (no installation needed)
uv run fcube --help
uv run fcube startproject MyProject

# Option 2: Install in editable mode
uv sync                         # Create venv and install dependencies
source .venv/bin/activate       # Activate the environment
fcube --help                    # Use the command

# Option 3: Run as Python module
python -m fcube --help
```

## Building the Package

### Build Distribution Files

```bash
# Build both wheel and source distribution
uv build

# Output will be in dist/
# - dist/fcube-1.0.0-py3-none-any.whl
# - dist/fcube-1.0.0.tar.gz
```

### Verify Package Contents

```bash
# List contents of the wheel
unzip -l dist/fcube-1.0.0-py3-none-any.whl

# Extract and inspect
mkdir -p test_pkg
cd test_pkg
unzip ../dist/fcube-1.0.0-py3-none-any.whl
```

### Test Local Installation

```bash
# Install from local wheel
uv tool install --force ./dist/fcube-1.0.0-py3-none-any.whl

# Test the installed command
fcube --version
fcube --help

# Uninstall
uv tool uninstall fcube
```

## Publishing to PyPI

### Prerequisites

1. Create accounts on:
   - PyPI: https://pypi.org/account/register/
   - TestPyPI: https://test.pypi.org/account/register/

2. Create API tokens:
   - PyPI: https://pypi.org/manage/account/token/
   - TestPyPI: https://test.pypi.org/manage/account/token/

3. Configure tokens:
   ```bash
   # Store in environment or use config file
   export PYPI_TOKEN="your-pypi-token"
   export TEST_PYPI_TOKEN="your-test-pypi-token"
   ```

### Publish to TestPyPI (Testing)

```bash
# Build the package
uv build

# Publish to TestPyPI
uv publish --token $TEST_PYPI_TOKEN \
  --publish-url https://test.pypi.org/legacy/

# Test installation from TestPyPI
uv tool install --index-url https://test.pypi.org/simple/ fcube

# Verify
fcube --version
```

### Publish to PyPI (Production)

```bash
# Ensure version is updated in pyproject.toml
# Build the package
uv build

# Publish to PyPI
uv publish --token $PYPI_TOKEN

# Or using environment variable UV_PUBLISH_TOKEN
UV_PUBLISH_TOKEN=$PYPI_TOKEN uv publish
```

After publishing, users can install with:
```bash
uv tool install fcube
```

## Version Management

### Update Version

Edit `pyproject.toml`:
```toml
[project]
version = "1.1.0"  # Update this
```

Also update `__init__.py`:
```python
__version__ = "1.1.0"
```

### Version Strategy

Follow [Semantic Versioning](https://semver.org/):
- **MAJOR** (1.0.0 → 2.0.0): Breaking changes
- **MINOR** (1.0.0 → 1.1.0): New features, backwards compatible
- **PATCH** (1.0.0 → 1.0.1): Bug fixes, backwards compatible

## GitHub Release Workflow

### Tag and Release

```bash
# Update version in files
# Commit changes
git add pyproject.toml fcube/__init__.py
git commit -m "Bump version to 1.1.0"

# Create and push tag
git tag -a v1.1.0 -m "Release version 1.1.0"
git push origin main
git push origin v1.1.0
```

### Create GitHub Release

1. Go to GitHub repository
2. Click "Releases" → "Create a new release"
3. Choose the tag (v1.1.0)
4. Write release notes
5. Attach distribution files from `dist/`
6. Publish release

## CI/CD Automation (Optional)

Create `.github/workflows/publish.yml`:

```yaml
name: Publish to PyPI

on:
  release:
    types: [published]

jobs:
  publish:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      
      - name: Install uv
        run: curl -LsSf https://astral.sh/uv/install.sh | sh
      
      - name: Build package
        run: uv build
      
      - name: Publish to PyPI
        env:
          UV_PUBLISH_TOKEN: ${{ secrets.PYPI_TOKEN }}
        run: uv publish
```

Add `PYPI_TOKEN` to GitHub repository secrets.

## Troubleshooting

### Package Structure Issues

If files are missing from the wheel:
```bash
# Check what's included
unzip -l dist/fcube-*.whl

# Verify pyproject.toml has correct force-include mappings
```

### Import Errors After Installation

```bash
# Ensure __init__.py is in the package
ls -la $(uv tool dir)/*/lib/python*/site-packages/fcube/
```

### Clean Build

```bash
# Remove old builds
rm -rf dist/ build/ *.egg-info

# Rebuild
uv build
```

## Package Structure

The package structure uses `force-include` to map the current directory to the `fcube` package:

```
fcube/                    # Repository root
├── pyproject.toml        # Package configuration
├── LICENSE               # MIT License
├── README.md             # Package documentation
├── __init__.py          → fcube/__init__.py
├── __main__.py          → fcube/__main__.py
├── cli.py               → fcube/cli.py
├── commands/            → fcube/commands/
├── templates/           → fcube/templates/
└── utils/               → fcube/utils/
```

## Development Checklist

Before publishing:

- [ ] Update version in `pyproject.toml`
- [ ] Update version in `__init__.py`
- [ ] Update `README.md` if needed
- [ ] Test local installation: `uv tool install --force .`
- [ ] Run commands: `fcube --help`, `fcube startproject test`
- [ ] Build package: `uv build`
- [ ] Verify wheel contents: `unzip -l dist/*.whl`
- [ ] Test on TestPyPI first
- [ ] Create git tag
- [ ] Push to GitHub
- [ ] Publish to PyPI
- [ ] Create GitHub release

## Useful Commands

```bash
# Development
uv run fcube --help                    # Run without installing
uv sync                                 # Install dependencies
source .venv/bin/activate              # Activate venv

# Building
uv build                                # Build wheel + sdist
uv build --wheel                        # Build wheel only

# Installing
uv tool install .                       # Install from current dir
uv tool install --force .              # Force reinstall
uv tool install --editable .           # Editable install

# Publishing
uv publish --dry-run                    # Test publish
uv publish --token $TOKEN              # Publish to PyPI
uv publish --publish-url https://test.pypi.org/legacy/  # TestPyPI

# Cleanup
uv tool uninstall fcube                # Uninstall tool
rm -rf dist/ build/ *.egg-info         # Clean build artifacts
```

## Resources

- [UV Documentation](https://docs.astral.sh/uv/)
- [Hatchling Build Backend](https://hatch.pypa.io/latest/config/build/)
- [PyPI Packaging Guide](https://packaging.python.org/)
- [Semantic Versioning](https://semver.org/)
