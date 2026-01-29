"""
FCube Plugins Package.

Contains modular "plugin" templates for optional features that can be
added to any FCube-generated project.

Architecture:
- Each plugin is a self-contained folder with templates and metadata
- Plugins follow the strategy pattern for extensibility
- The `addplugin` command discovers and installs plugins

Available Plugins:
- referral: User referral system with configurable completion strategies

Usage:
    fcube addplugin referral
    fcube addplugin --list  # List available plugins
"""

from pathlib import Path
from typing import Dict, List, Optional
from dataclasses import dataclass


@dataclass
class PluginMetadata:
    """Metadata for a plugin module."""
    name: str
    description: str
    version: str
    dependencies: List[str]  # Required modules (e.g., ["user"])
    files_generated: List[str]  # List of files that will be created
    config_required: bool  # Whether plugin needs configuration
    post_install_notes: str  # Instructions after installation


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


# Auto-discover and register plugins
def _discover_plugins() -> None:
    """Discover and register all available plugins."""
    from .referral import PLUGIN_METADATA as referral_metadata
    register_plugin(referral_metadata)
    
    # Future plugins will be registered here:
    # from .notifications import PLUGIN_METADATA as notifications_metadata
    # register_plugin(notifications_metadata)


# Initialize registry on import
_discover_plugins()

__all__ = [
    "PluginMetadata",
    "PLUGIN_REGISTRY",
    "get_available_plugins",
    "get_plugin",
    "register_plugin",
]
