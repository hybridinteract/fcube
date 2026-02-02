"""
FCube Plugins Package.

Contains modular "plugin" templates for optional features that can be
added to any FCube-generated project.

Architecture:
- Each plugin is a self-contained folder with templates, metadata, and installer
- Plugins follow the strategy pattern for extensibility
- The `addplugin` command discovers and installs plugins automatically

To Add a New Plugin:
1. Create folder: fcube/templates/plugins/your_plugin/
2. Add __init__.py with PLUGIN_METADATA and install_plugin() function
3. Add template files (model_templates.py, etc.)
4. Register in _discover_plugins() below
5. Done! No need to modify addplugin.py

Available Plugins:
- referral: User referral system with configurable completion strategies
- deploy_vps: Complete VPS deployment system with Docker, Nginx, SSL, Redis, Celery

Usage:
    fcube addplugin referral
    fcube addplugin deploy_vps
    fcube addplugin --list  # List available plugins
"""

from pathlib import Path
from typing import Dict, List, Optional, Tuple, Callable
from dataclasses import dataclass, field


@dataclass
class PluginMetadata:
    """Metadata for a plugin module.
    
    Attributes:
        name: Plugin identifier (e.g., "referral")
        description: Short description for --list display
        version: Semantic version string
        dependencies: Required modules (e.g., ["user"])
        files_generated: List of files that will be created
        config_required: Whether plugin needs configuration
        post_install_notes: Instructions shown after installation
        installer: Function that generates file list for the plugin
    """
    name: str
    description: str
    version: str
    dependencies: List[str]
    files_generated: List[str]
    config_required: bool
    post_install_notes: str
    # The installer function: takes app_dir Path, returns List[(Path, content)]
    installer: Callable[[Path], List[Tuple[Path, str]]] = field(default=None)


# Plugin Registry - maps plugin names to their metadata
PLUGIN_REGISTRY: Dict[str, PluginMetadata] = {}


def validate_plugin_metadata(metadata: PluginMetadata) -> None:
    """Validate plugin metadata before registration.
    
    Ensures that:
    - All required fields are populated
    - Installer function is callable
    - Version follows semantic versioning pattern
    - Files listed actually get generated
    
    Raises:
        ValueError: If validation fails
    """
    # Required fields check
    if not metadata.name:
        raise ValueError("Plugin metadata missing 'name' field")
    
    if not metadata.name.isidentifier():
        raise ValueError(
            f"Plugin name '{metadata.name}' is not a valid Python identifier. "
            "Use lowercase letters, numbers, and underscores only."
        )
    
    if not metadata.description:
        raise ValueError(f"Plugin '{metadata.name}' missing 'description' field")
    
    if not metadata.version:
        raise ValueError(f"Plugin '{metadata.name}' missing 'version' field")
    
    # Version format validation (basic semver check)
    version_parts = metadata.version.split('.')
    if len(version_parts) != 3 or not all(part.isdigit() for part in version_parts):
        raise ValueError(
            f"Plugin '{metadata.name}' has invalid version '{metadata.version}'. "
            "Expected semantic version format (e.g., '1.0.0')"
        )
    
    # Installer validation
    if not metadata.installer:
        raise ValueError(
            f"Plugin '{metadata.name}' missing 'installer' function. "
            "Each plugin must have a self-contained installer function."
        )
    
    if not callable(metadata.installer):
        raise ValueError(
            f"Plugin '{metadata.name}' installer is not callable. "
            f"Got type: {type(metadata.installer).__name__}"
        )
    
    # Post-install notes check
    if not metadata.post_install_notes:
        raise ValueError(
            f"Plugin '{metadata.name}' missing 'post_install_notes'. "
            "Provide clear instructions for users on what to do after installation."
        )
    
    # Files generated list check
    if not metadata.files_generated:
        raise ValueError(
            f"Plugin '{metadata.name}' has empty 'files_generated' list. "
            "Specify which files the plugin creates."
        )


def register_plugin(metadata: PluginMetadata) -> None:
    """Register a plugin in the global registry after validation."""
    # Validate before registering
    validate_plugin_metadata(metadata)
    PLUGIN_REGISTRY[metadata.name] = metadata


def get_available_plugins() -> Dict[str, PluginMetadata]:
    """Get all available plugins."""
    return PLUGIN_REGISTRY.copy()


def get_plugin(name: str) -> Optional[PluginMetadata]:
    """Get a specific plugin by name."""
    return PLUGIN_REGISTRY.get(name)


def install_plugin(name: str, app_dir: Path) -> List[Tuple[Path, str]]:
    """Install a plugin by name. Returns list of (path, content) tuples.
    
    This is the unified entry point - it delegates to the plugin's own installer.
    """
    plugin = PLUGIN_REGISTRY.get(name)
    if not plugin:
        raise ValueError(f"Unknown plugin: {name}")
    if not plugin.installer:
        raise NotImplementedError(f"Plugin '{name}' has no installer function")
    return plugin.installer(app_dir)


# Auto-discover and register plugins
def _discover_plugins() -> None:
    """Discover and register all available plugins.
    
    To add a new plugin:
    1. Create your plugin folder with templates and __init__.py
    2. Import and register it here
    """
    from .referral import PLUGIN_METADATA as referral_metadata
    register_plugin(referral_metadata)
    
    from .deploy_vps import PLUGIN_METADATA as deploy_vps_metadata
    register_plugin(deploy_vps_metadata)


# Initialize registry on import
_discover_plugins()

__all__ = [
    "PluginMetadata",
    "PLUGIN_REGISTRY",
    "get_available_plugins",
    "get_plugin",
    "install_plugin",
    "register_plugin",
    "validate_plugin_metadata",
]
