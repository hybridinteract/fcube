# Plugin System Quick Reference

## New Features

### 1. Automatic Plugin Validation ✅

**What it does:** Validates all plugin metadata during registration

**When it happens:** Automatically at `_discover_plugins()` time

**What it checks:**
```
✓ name         - Valid Python identifier (e.g., "my_plugin")
✓ description  - Not empty
✓ version      - Semantic version (e.g., "1.0.0")
✓ installer    - Is callable
✓ post_install_notes - Not empty
✓ files_generated    - Not empty list
```

**Error example:**
```bash
ValueError: Plugin 'my-plugin' is not a valid Python identifier.
Use lowercase letters, numbers, and underscores only.
```

---

### 2. Dry-Run Mode 🔍

**What it does:** Preview plugin installation without creating files

**Usage:**
```bash
fcube addplugin <name> --dry-run
```

**Examples:**
```bash
# Preview referral plugin
fcube addplugin referral --dry-run

# List all plugins first
fcube addplugin --list

# Preview, review, then install
fcube addplugin referral --dry-run  # See what would happen
fcube addplugin referral            # Actually install
```

**Output includes:**
- 📦 Table of all files (path, size, status)
- 📊 Summary (plugin name, version, total files, total size)
- 📝 Post-install steps preview
- ℹ️  Clear "this was a dry run" message

---

## Command Reference

### List Available Plugins
```bash
fcube addplugin --list
fcube addplugin -l
```

### Preview Plugin Installation
```bash
fcube addplugin <name> --dry-run
```

### Install Plugin
```bash
fcube addplugin <name>
fcube addplugin <name> --force          # Overwrite existing
fcube addplugin <name> --dir my_app     # Custom directory
```

### Combined Flags
```bash
fcube addplugin referral --dry-run --dir my_app
```

---

## For Plugin Developers

### Valid Plugin Metadata

```python
from pathlib import Path
from typing import List, Tuple
from .. import PluginMetadata

def install_my_plugin(app_dir: Path) -> List[Tuple[Path, str]]:
    """Generate files for the plugin."""
    plugin_dir = app_dir / "my_plugin"
    return [
        (plugin_dir / "__init__.py", generate_init()),
        (plugin_dir / "models.py", generate_models()),
        # ... more files
    ]

PLUGIN_METADATA = PluginMetadata(
    name="my_plugin",                    # ✅ Valid identifier
    description="Does something cool",   # ✅ Clear description
    version="1.0.0",                     # ✅ Semver format
    dependencies=["user"],               # ✅ List dependencies
    files_generated=[                    # ✅ List all files
        "app/my_plugin/__init__.py",
        "app/my_plugin/models.py",
    ],
    config_required=False,
    post_install_notes="""               # ✅ Clear instructions
1. Update apis/v1.py to include routes
2. Run: alembic revision --autogenerate
3. Run: alembic upgrade head
    """,
    installer=install_my_plugin         # ✅ Callable function
)
```

### Validation Checklist

Before registering your plugin, ensure:

- [ ] Name uses only lowercase, numbers, underscores
- [ ] Description explains what the plugin does
- [ ] Version is "X.Y.Z" format (semantic versioning)
- [ ] All dependencies are listed
- [ ] All generated files are listed
- [ ] Post-install notes are complete and clear
- [ ] Installer function is defined and callable

### Testing Your Plugin

```bash
# 1. Register plugin in templates/plugins/__init__.py
from .my_plugin import PLUGIN_METADATA as my_plugin_metadata
register_plugin(my_plugin_metadata)

# 2. Test listing (validates automatically)
fcube addplugin --list

# 3. Test dry-run
fcube addplugin my_plugin --dry-run

# 4. Review output, then install for real
fcube addplugin my_plugin
```

---

## Troubleshooting

### "Plugin name is not a valid Python identifier"
**Problem:** Plugin name contains hyphens, spaces, or starts with number

**Fix:** Use only lowercase letters, numbers, underscores
```python
# ❌ Bad
name="my-plugin"
name="my plugin"
name="2plugin"

# ✅ Good
name="my_plugin"
name="myplugin"
name="plugin2"
```

### "Invalid version format"
**Problem:** Version doesn't follow X.Y.Z format

**Fix:** Use semantic versioning
```python
# ❌ Bad
version="1.0"
version="v1.0.0"
version="1.0.0-beta"

# ✅ Good
version="1.0.0"
version="2.1.3"
version="0.0.1"
```

### "Installer is not callable"
**Problem:** Installer is not a function

**Fix:** Pass the function reference (not the result)
```python
# ❌ Bad
installer=install_my_plugin()  # Called it!

# ✅ Good
installer=install_my_plugin    # Just the reference
```

### "Plugin missing post_install_notes"
**Problem:** No instructions provided

**Fix:** Add clear post-install steps
```python
post_install_notes="""
1. Add these routes to apis/v1.py
2. Update alembic_models_import.py
3. Run migrations
"""
```

---

## Best Practices

### DO ✅
- Use `--dry-run` before installing in production
- Validate your plugin metadata is complete
- Provide clear post-install instructions
- List all files your plugin generates
- Use semantic versioning

### DON'T ❌
- Install plugins without reviewing with --dry-run
- Use hyphens or spaces in plugin names
- Forget to list dependencies
- Leave post-install notes empty
- Use non-standard version formats

---

## Quick Start Workflow

### For Users
```bash
# 1. See what's available
fcube addplugin --list

# 2. Preview before installing
fcube addplugin referral --dry-run

# 3. Review the output

# 4. Install for real
fcube addplugin referral

# 5. Follow post-install steps
```

### For Developers
```bash
# 1. Create plugin folder
mkdir -p templates/plugins/my_plugin

# 2. Add templates and __init__.py with PLUGIN_METADATA

# 3. Register in templates/plugins/__init__.py

# 4. Test validation
fcube addplugin --list

# 5. Test installation
fcube addplugin my_plugin --dry-run

# 6. Fix any issues, repeat steps 4-5

# 7. Done!
```

---

## Related Documentation

- **Full details:** `PLUGIN_IMPROVEMENTS.md`
- **Implementation summary:** `IMPROVEMENTS_SUMMARY.md`
- **Main README:** `README.md`
- **Example plugin:** `templates/plugins/referral/`

---

**Version:** 1.0.0  
**Last Updated:** 2026-02-01
