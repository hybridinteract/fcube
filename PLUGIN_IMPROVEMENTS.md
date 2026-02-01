# Plugin System Improvements

## Overview

This document describes the plugin system enhancements implemented to improve quality, safety, and user experience.

---

## 1. Plugin Metadata Validation ✅

### What It Does
Automatically validates plugin metadata during registration to ensure all plugins meet quality standards.

### Validation Checks

#### Required Fields
- ✅ **name**: Must be a valid Python identifier (lowercase, underscores)
- ✅ **description**: Clear description of what the plugin does
- ✅ **version**: Semantic versioning format (e.g., "1.0.0")
- ✅ **installer**: Must be a callable function
- ✅ **post_install_notes**: Clear instructions for users
- ✅ **files_generated**: Non-empty list of files

#### Validation Rules
```python
# Name validation
if not metadata.name.isidentifier():
    raise ValueError("Plugin name must be a valid Python identifier")

# Version validation (semver)
version_parts = metadata.version.split('.')
if len(version_parts) != 3 or not all(part.isdigit() for part in version_parts):
    raise ValueError("Invalid version format. Expected: X.Y.Z")

# Installer validation
if not callable(metadata.installer):
    raise ValueError("Installer must be a callable function")
```

### When Validation Occurs
Validation happens automatically at plugin registration time:

```python
# In templates/plugins/__init__.py
def register_plugin(metadata: PluginMetadata) -> None:
    """Register a plugin after validation."""
    validate_plugin_metadata(metadata)  # ← Validates here
    PLUGIN_REGISTRY[metadata.name] = metadata
```

### Benefits
- ✅ **Catches errors early** - Invalid plugins fail at import time, not runtime
- ✅ **Improves plugin quality** - Ensures all plugins follow standards
- ✅ **Clear error messages** - Tells plugin authors exactly what's wrong
- ✅ **Prevents broken installations** - Users never encounter incomplete plugins

### Example Error Messages
```bash
❌ ValueError: Plugin 'my-plugin' is not a valid Python identifier.
   Use lowercase letters, numbers, and underscores only.

❌ ValueError: Plugin 'myplugin' has invalid version '1.0'.
   Expected semantic version format (e.g., '1.0.0')

❌ ValueError: Plugin 'myplugin' missing 'post_install_notes'.
   Provide clear instructions for users on what to do after installation.
```

---

## 2. Dry-Run Mode 🔍

### What It Does
Allows users to preview exactly what files will be created before actually installing a plugin.

### Usage

```bash
# Preview what the referral plugin would create
fcube addplugin referral --dry-run

# List available plugins first
fcube addplugin --list

# Preview, then install for real
fcube addplugin referral --dry-run  # Review first
fcube addplugin referral            # Then install
```

### Output Example

```
🔍 DRY RUN MODE - No files will be created

📋 Preview: Plugin 'referral' would create:

┌─────────────────────────────────────────────┬─────────┬─────────────────┐
│ File Path                                   │    Size │ Status          │
├─────────────────────────────────────────────┼─────────┼─────────────────┤
│ app/referral/__init__.py                    │  0.6 KB │ New file        │
│ app/referral/models.py                      │  8.0 KB │ New file        │
│ app/referral/config.py                      │  7.0 KB │ New file        │
│ app/referral/strategies.py                  │  3.5 KB │ New file        │
│ app/referral/exceptions.py                  │  2.3 KB │ New file        │
│ app/referral/dependencies.py                │  2.1 KB │ New file        │
│ app/referral/tasks.py                       │  4.0 KB │ New file        │
│ app/referral/schemas/__init__.py            │  0.3 KB │ New file        │
│ app/referral/schemas/referral_schemas.py    │  7.4 KB │ New file        │
│ app/referral/crud/__init__.py               │  0.2 KB │ New file        │
│ app/referral/crud/referral_crud.py          │ 12.9 KB │ New file        │
│ app/referral/services/__init__.py           │  0.2 KB │ New file        │
│ app/referral/services/referral_service.py   │ 13.1 KB │ New file        │
│ app/referral/routes/__init__.py             │  0.3 KB │ New file        │
│ app/referral/routes/referral_routes.py      │  8.2 KB │ New file        │
│ app/referral/routes/referral_admin_routes.py│  8.2 KB │ New file        │
└─────────────────────────────────────────────┴─────────┴─────────────────┘

┌───────────────┬──────────────────────────┐
│ Plugin:       │ referral                 │
│ Version:      │ 1.0.0                    │
│ Total Files:  │ 16                       │
│ Total Size:   │ 78.3 KB                  │
│ Target Dir:   │ app/referral             │
└───────────────┴──────────────────────────┘

┌─ 📝 Post-Install Steps (Preview) ─┐
│                                    │
│ 1. Add referral_code to User      │
│ 2. Update apis/v1.py               │
│ 3. Update alembic_models_import.py │
│ 4. Run migrations                  │
└────────────────────────────────────┘

ℹ️  This was a dry run - no files were created.
To install for real, run: fcube addplugin referral
```

### Features

#### 1. **File Preview Table**
- Shows all files that would be created
- Displays file sizes (in bytes or KB)
- Indicates if files already exist ("Would overwrite" vs "New file")

#### 2. **Summary Statistics**
- Plugin name and version
- Total number of files
- Total size of all files
- Target installation directory

#### 3. **Post-Install Preview**
- Shows what manual steps would be needed
- Same information that would appear after real installation

#### 4. **Safety Features**
- **Zero side effects** - No files or directories are created
- **No validation skipped** - All checks still run (dependencies, conflicts, etc.)
- **Clear messaging** - Users know it's a preview

### Benefits

✅ **Safe exploration** - Try before you commit  
✅ **Understand impact** - See exactly what changes  
✅ **Avoid mistakes** - Review file sizes and paths  
✅ **Plan integration** - See post-install steps ahead of time  
✅ **Disk space check** - Know total size before installing  

### Use Cases

#### 1. **First-Time Users**
```bash
# Exploring what a plugin does
fcube addplugin referral --dry-run
```

#### 2. **CI/CD Pipelines**
```bash
# Validate plugin in CI before deploying
fcube addplugin myplugin --dry-run
if [[ $? -eq 0 ]]; then
    fcube addplugin myplugin
fi
```

#### 3. **Plugin Development**
```bash
# Test your plugin installer without creating files
fcube addplugin my_new_plugin --dry-run
```

#### 4. **Documentation**
```bash
# Generate documentation showing what files a plugin creates
fcube addplugin referral --dry-run > docs/referral-files.txt
```

---

## Implementation Details

### Code Changes

#### 1. **Validation Function** (`templates/plugins/__init__.py`)
```python
def validate_plugin_metadata(metadata: PluginMetadata) -> None:
    """Validate plugin metadata before registration."""
    # Name validation
    if not metadata.name.isidentifier():
        raise ValueError(...)
    
    # Version validation (semver)
    if not valid_semver(metadata.version):
        raise ValueError(...)
    
    # Installer validation
    if not callable(metadata.installer):
        raise ValueError(...)
    
    # ... more checks
```

#### 2. **Dry-Run Logic** (`commands/addplugin.py`)
```python
def addplugin_command(..., dry_run: bool = False):
    # ... existing checks ...
    
    # Generate files
    files_to_create = install_plugin(plugin_name, app_dir)
    
    if dry_run:
        # Show preview table
        show_preview_table(files_to_create)
        # Exit early - no files created
        return
    
    # Normal installation
    create_files(files_to_create)
```

#### 3. **CLI Interface** (`cli.py`)
```python
@app.command("addplugin")
def addplugin(
    ...,
    dry_run: bool = typer.Option(
        False,
        "--dry-run",
        help="Preview files without creating them"
    ),
):
    addplugin_command(..., dry_run=dry_run)
```

---

## Testing

### Manual Testing

```bash
# 1. Test validation with invalid plugin
# Should fail at registration with clear error

# 2. Test dry-run mode
fcube addplugin referral --dry-run
# Should show preview without creating files

# 3. Verify no files created
ls app/referral
# Should not exist

# 4. Test actual installation after dry-run
fcube addplugin referral
# Should create all files

# 5. Test dry-run on existing plugin
fcube addplugin referral --dry-run
# Should show "Would overwrite" status
```

### Automated Testing (Future)

```python
def test_plugin_validation():
    """Test that invalid plugins are rejected."""
    invalid_metadata = PluginMetadata(
        name="my-invalid-plugin",  # Invalid: contains hyphen
        # ... other fields
    )
    
    with pytest.raises(ValueError, match="valid Python identifier"):
        register_plugin(invalid_metadata)


def test_dry_run_creates_no_files(tmp_path):
    """Test that dry-run doesn't create files."""
    # Run with dry_run=True
    addplugin_command("referral", dry_run=True)
    
    # Assert no files created
    assert not (tmp_path / "app" / "referral").exists()


def test_dry_run_shows_preview(capsys):
    """Test that dry-run displays preview."""
    addplugin_command("referral", dry_run=True)
    
    captured = capsys.readouterr()
    assert "DRY RUN MODE" in captured.out
    assert "Files Preview" in captured.out
```

---

## Future Enhancements

### 1. **Plugin Version Compatibility**
```python
@dataclass
class PluginMetadata:
    # ... existing fields ...
    min_fcube_version: str = "0.1.0"  # Minimum FCube version required
    max_fcube_version: Optional[str] = None  # Maximum (for breaking changes)
```

### 2. **Dependency Graph Validation**
```python
def validate_dependency_graph():
    """Ensure no circular dependencies between plugins."""
    # Detect cycles in plugin dependencies
```

### 3. **Plugin Testing Framework**
```python
def test_plugin_generates_valid_python(plugin_name):
    """Validate that all generated files are syntactically valid."""
    files = install_plugin(plugin_name, tmp_path)
    for path, content in files:
        compile(content, str(path), 'exec')  # Raises SyntaxError if invalid
```

### 4. **Interactive Dry-Run**
```bash
fcube addplugin referral --dry-run --interactive
# Show preview with option to proceed:
# ❓ Install this plugin? [y/N]:
```

### 5. **JSON Output for CI/CD**
```bash
fcube addplugin referral --dry-run --json > preview.json
# Output structured data for programmatic use
```

---

## Migration Guide for Plugin Authors

### If You're Creating a New Plugin

Your plugin will automatically be validated. Ensure:

1. ✅ **Name** uses valid Python identifier (lowercase, underscores)
2. ✅ **Version** follows semver (e.g., "1.0.0")
3. ✅ **Description** clearly explains what the plugin does
4. ✅ **Installer** is a callable function
5. ✅ **Post-install notes** provide clear next steps
6. ✅ **Files list** is complete and accurate

### Example of Valid Plugin Metadata

```python
from pathlib import Path
from typing import List, Tuple
from .. import PluginMetadata

def install_my_plugin(app_dir: Path) -> List[Tuple[Path, str]]:
    """Self-contained installer."""
    return [
        (app_dir / "myplugin" / "__init__.py", "# Init content"),
        (app_dir / "myplugin" / "models.py", "# Model content"),
    ]

PLUGIN_METADATA = PluginMetadata(
    name="my_plugin",           # ✅ Valid identifier
    description="Does something awesome",  # ✅ Clear description
    version="1.0.0",            # ✅ Semantic version
    dependencies=["user"],      # ✅ Clear dependencies
    files_generated=[           # ✅ Complete file list
        "app/my_plugin/__init__.py",
        "app/my_plugin/models.py",
    ],
    config_required=False,
    post_install_notes="""      # ✅ Helpful instructions
1. Update apis/v1.py
2. Run migrations
    """,
    installer=install_my_plugin  # ✅ Callable function
)
```

---

## Summary

### What Changed
1. ✅ Added **automatic plugin validation** at registration
2. ✅ Implemented **--dry-run mode** for safe previews
3. ✅ Enhanced **error messages** with clear guidance
4. ✅ Improved **user experience** with detailed previews

### Benefits
- 🛡️ **Quality assurance** - Invalid plugins caught early
- 🔍 **Transparency** - Users see exactly what will happen
- 🚀 **Confidence** - Try before committing
- 📚 **Documentation** - Preview serves as documentation

### No Breaking Changes
- ✅ Existing plugins continue to work
- ✅ No API changes required
- ✅ Backward compatible
- ✅ Additive improvements only

---

## Questions?

For more information, see:
- Main README: `README.md`
- Plugin development guide: `README.md` (section: Adding New Plugins)
- Example plugin: `templates/plugins/referral/`
