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

Usage:
    fcube addplugin referral
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


def register_plugin(metadata: PluginMetadata) -> None:
    """Register a plugin in the global registry."""
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
    
    # ──────────────────────────────────────────────────────────────────────
    # ADD NEW PLUGINS HERE:
    # 
    # from .notifications import PLUGIN_METADATA as notifications_metadata
    # register_plugin(notifications_metadata)
    #
    # from .audit import PLUGIN_METADATA as audit_metadata
    # register_plugin(audit_metadata)
    # ──────────────────────────────────────────────────────────────────────


# Initialize registry on import
_discover_plugins()

__all__ = [
    "PluginMetadata",
    "PLUGIN_REGISTRY",
    "get_available_plugins",
    "get_plugin",
    "install_plugin",
    "register_plugin",
]
