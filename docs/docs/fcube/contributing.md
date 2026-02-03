# Contributing to FCube

How to contribute to FCube development.

---

## Getting Started

### Prerequisites

- Python 3.9+
- Git
- A GitHub account

### Fork and Clone

```bash
# Fork the repository on GitHub, then:
git clone https://github.com/YOUR_USERNAME/fcube.git
cd fcube

# Add upstream remote
git remote add upstream https://github.com/amal-babu-git/fcube.git
```

### Set Up Development Environment

```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate

# Install in development mode
pip install -e .

# Using uv (recommended for development)
uv sync
source .venv/bin/activate

# Run tests to verify setup
pytest
```

---

## Development Workflow

### 1. Create a Branch

```bash
# Sync with upstream
git fetch upstream
git checkout main
git merge upstream/main

# Create feature branch
git checkout -b feature/my-feature
```

### 2. Make Changes

Follow the code style guidelines and add tests for new functionality.

### 3. Run Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=fcube

# Run specific test file
pytest tests/test_cli.py
```

### 4. Commit Changes

```bash
# Stage changes
git add .

# Commit with conventional message
git commit -m "feat(cli): add dry-run mode to addplugin"
```

### 5. Push and Create PR

```bash
git push origin feature/my-feature
```

Then create a Pull Request on GitHub.

---

## Code Style

### Python

We use these tools:

| Tool | Purpose |
|------|---------|
| `ruff` | Linting |
| `black` | Formatting |
| `mypy` | Type checking |

```bash
# Format code
black fcube/

# Lint code
ruff check fcube/

# Type check
mypy fcube/
```

### Commit Messages

Follow [Conventional Commits](https://www.conventionalcommits.org/):

```
<type>(<scope>): <subject>

<body>

<footer>
```

**Types:**

- `feat` — New feature
- `fix` — Bug fix
- `docs` — Documentation
- `style` — Formatting
- `refactor` — Code restructuring
- `test` — Adding tests
- `chore` — Maintenance

**Examples:**

```
feat(cli): add startproject command
fix(templates): correct import path in routes
docs(readme): update installation instructions
```

---

## Adding Commands

### 1. Create Command Function

```python
# fcube/commands/mycommand.py
from pathlib import Path
from typing import List, Tuple

from fcube.utils.helpers import write_file


def execute_mycommand(
    name: str,
    app_dir: Path,
) -> List[Path]:
    """
    Execute mycommand logic.
    
    Args:
        name: Name parameter
        app_dir: Application directory
    
    Returns:
        List of created files
    """
    files_created = []
    
    # Generate files
    content = generate_content(name)
    file_path = app_dir / f"{name}.py"
    write_file(file_path, content)
    files_created.append(file_path)
    
    return files_created
```

### 2. Register in CLI

```python
# fcube/cli.py
import typer
from fcube.commands.mycommand import execute_mycommand

app = typer.Typer()


@app.command("mycommand")
def mycommand(
    name: str = typer.Argument(..., help="Name parameter"),
    dry_run: bool = typer.Option(False, "--dry-run", help="Preview changes"),
):
    """Description of mycommand."""
    app_dir = Path.cwd() / "app"
    
    if dry_run:
        typer.echo("Would create files...")
        return
    
    files = execute_mycommand(name, app_dir)
    
    for file in files:
        typer.echo(f"✓ Created {file}")
```

### 3. Add Tests

```python
# tests/test_mycommand.py
import pytest
from pathlib import Path
from fcube.commands.mycommand import execute_mycommand


def test_mycommand_creates_file(tmp_path):
    """Test that mycommand creates expected file."""
    app_dir = tmp_path / "app"
    app_dir.mkdir()
    
    files = execute_mycommand("test", app_dir)
    
    assert len(files) == 1
    assert files[0].exists()
    assert "test" in files[0].read_text()
```

---

## Adding Plugins

### 1. Create Plugin Directory

```
fcube/templates/plugins/my_plugin/
├── __init__.py
├── templates.py
└── README.md
```

### 2. Define Metadata

```python
# __init__.py
from dataclasses import dataclass
from pathlib import Path
from typing import List, Tuple

from fcube.templates.plugins import PluginMetadata
from .templates import generate_model, generate_schema, generate_service


def install_my_plugin(app_dir: Path) -> List[Tuple[Path, str]]:
    """Install plugin files."""
    return [
        (app_dir / "models" / "my_plugin.py", generate_model()),
        (app_dir / "schemas" / "my_plugin.py", generate_schema()),
        (app_dir / "services" / "my_plugin.py", generate_service()),
    ]


PLUGIN_METADATA = PluginMetadata(
    name="my_plugin",
    description="What this plugin does",
    version="1.0.0",
    dependencies=[],
    files_generated=[
        "app/models/my_plugin.py",
        "app/schemas/my_plugin.py",
        "app/services/my_plugin.py",
    ],
    config_required=False,
    post_install_notes="Post-installation instructions",
    installer=install_my_plugin,
)
```

### 3. Create Templates

```python
# templates.py
def generate_model() -> str:
    return '''from sqlalchemy import ...
# Model code
'''


def generate_schema() -> str:
    return '''from pydantic import ...
# Schema code
'''


def generate_service() -> str:
    return '''# Service code
'''
```

### 4. Register Plugin

```python
# fcube/templates/plugins/__init__.py
def _discover_plugins() -> None:
    from .my_plugin import PLUGIN_METADATA as my_plugin_metadata
    register_plugin(my_plugin_metadata)
```

### 5. Add Tests

```python
# tests/test_plugins/test_my_plugin.py
def test_my_plugin_installs(tmp_path):
    """Test plugin installation."""
    from fcube.templates.plugins.my_plugin import install_my_plugin
    
    app_dir = tmp_path / "app"
    app_dir.mkdir()
    
    files = install_my_plugin(app_dir)
    
    assert len(files) == 3
    for path, content in files:
        assert content  # Content is not empty
```

---

## Testing

### Running Tests

```bash
# All tests
pytest

# With coverage
pytest --cov=fcube --cov-report=html

# Specific test
pytest tests/test_cli.py::test_startproject
```

### Test Structure

```
tests/
├── conftest.py              # Shared fixtures
├── test_cli.py              # CLI integration tests
├── test_commands/
│   ├── test_startproject.py
│   ├── test_addmodule.py
│   └── test_addplugin.py
├── test_templates/
│   ├── test_model_templates.py
│   └── test_schema_templates.py
└── test_plugins/
    ├── test_referral.py
    └── test_deploy_vps.py
```

---

## Pull Request Checklist

Before submitting a PR, ensure:

- [ ] Tests pass (`pytest`)
- [ ] Code is formatted (`black fcube/`)
- [ ] Linting passes (`ruff check fcube/`)
- [ ] Types are correct (`mypy fcube/`)
- [ ] Documentation is updated if needed
- [ ] Commit messages follow conventions
- [ ] PR description explains changes

---

## Need Help?

- **Questions**: Open a GitHub Discussion
- **Bugs**: Open a GitHub Issue
- **Features**: Open an Issue first to discuss
