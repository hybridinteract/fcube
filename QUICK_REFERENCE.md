# FCube - Quick Reference Card

## Install Globally

```bash
# From GitHub
uv tool install git+https://github.com/YOUR_USERNAME/fcube.git

# From local clone
git clone https://github.com/YOUR_USERNAME/fcube.git
cd fcube && uv tool install .

# From PyPI (after publishing)
uv tool install fcube
```

## Verify Installation

```bash
fcube --version  # Should show: FCube CLI version 1.0.0
fcube --help     # Show all commands
```

## Update/Reinstall

```bash
uv tool install --force git+https://github.com/YOUR_USERNAME/fcube.git
# or
cd fcube && uv tool install --force .
```

## Uninstall

```bash
uv tool uninstall fcube
```

## Development Mode

```bash
cd fcube
uv run fcube --help              # Run without installing
uv sync                          # Create venv + install deps
source .venv/bin/activate        # Activate venv
```

## Build & Test

```bash
uv build                     # Build package
./test_installation.sh       # Run all tests
```

## Publish to PyPI

```bash
uv build
uv publish --token $PYPI_TOKEN
```

## Common Commands

```bash
fcube startproject MyAPI
fcube adduser --auth-type email
fcube addplugin referral
fcube startmodule Product
fcube addentity product review
fcube listmodules
```

## Files

- **README.md** - Main documentation
- **INSTALL_AND_PUBLISH.md** - Publishing guide
- **SETUP_COMPLETE.md** - Setup summary
- **test_installation.sh** - Test script
- **pyproject.toml** - Package config
- **LICENSE** - MIT License

## Support

- Repository: https://github.com/YOUR_USERNAME/fcube
- Issues: https://github.com/YOUR_USERNAME/fcube/issues
