"""
Add Plugin Command - Universal command for adding plugin modules.

Discovers and installs pre-built plugin modules. Each plugin is self-contained
in its own folder under templates/plugins/ with its own installer function.

Available Plugins:
- referral: User referral system with completion strategies
- (future) notifications: Push/email notification system
- (future) audit: Audit logging system

Usage:
    fcube addplugin referral
    fcube addplugin --list  # Show available plugins

Contributing New Plugins:
1. Create folder: fcube/templates/plugins/your_plugin/
2. Add __init__.py with PLUGIN_METADATA (including installer function)
3. Add template files (model_templates.py, etc.)
4. Register in fcube/templates/plugins/__init__.py (_discover_plugins)
5. Done! This file does NOT need to be modified.
"""

import typer
from pathlib import Path
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.tree import Tree
from typing import List, Tuple

from ..utils.helpers import (
    ensure_directory,
    write_file,
)
from ..templates.plugins import (
    get_available_plugins,
    get_plugin,
    install_plugin,
    PluginMetadata,
)

console = Console()


def list_available_plugins():
    """Display all available plugins."""
    plugins = get_available_plugins()
    
    if not plugins:
        console.print("[yellow]No plugins available.[/yellow]")
        return
    
    table = Table(
        title="🔌 Available FCube Plugins",
        show_header=True,
        header_style="bold cyan"
    )
    table.add_column("Plugin", style="bold green")
    table.add_column("Version", style="dim")
    table.add_column("Description")
    table.add_column("Dependencies", style="yellow")
    
    for name, meta in plugins.items():
        deps = ", ".join(meta.dependencies) if meta.dependencies else "None"
        table.add_row(name, meta.version, meta.description, deps)
    
    console.print(table)
    console.print()
    console.print("[dim]Usage: fcube addplugin <plugin_name>[/dim]")


def addplugin_command(
    plugin_name: str = None,
    directory: str = "app",
    force: bool = False,
    list_plugins: bool = False,
    dry_run: bool = False,
):
    """
    Add a plugin module to your project.
    
    Plugins are self-contained modules that extend your project with
    pre-built features like referral systems, notifications, etc.
    
    Args:
        plugin_name: Name of the plugin to install
        directory: Target directory (default: "app")
        force: Overwrite existing files
        list_plugins: Show available plugins
        dry_run: Preview files without creating them
    """
    # Handle --list flag
    if list_plugins or plugin_name is None:
        list_available_plugins()
        return
    
    console.print(f"\n[bold blue]🧊 FCube CLI - Adding Plugin: {plugin_name}[/bold blue]\n")
    
    # Check if plugin exists
    metadata = get_plugin(plugin_name)
    if not metadata:
        console.print(f"[bold red]❌ Error:[/bold red] Unknown plugin '{plugin_name}'")
        console.print()
        list_available_plugins()
        raise typer.Exit(1)
    
    # Check if plugin has installer
    if not metadata.installer:
        console.print(f"[bold red]❌ Error:[/bold red] Plugin '{plugin_name}' has no installer function")
        console.print(f"[yellow]💡 Tip:[/yellow] The plugin needs an 'installer' function in its metadata")
        raise typer.Exit(1)
    
    # Define paths
    base_dir = Path.cwd()
    app_dir = base_dir / directory
    
    # Check if app directory exists
    if not app_dir.exists():
        console.print(f"[bold red]❌ Error:[/bold red] Directory '{directory}' not found.")
        console.print(f"[yellow]💡 Tip:[/yellow] Make sure you're in the project root.")
        raise typer.Exit(1)
    
    # Check dependencies
    for dep in metadata.dependencies:
        dep_dir = app_dir / dep
        if not dep_dir.exists():
            console.print(f"[bold red]❌ Error:[/bold red] Required module '{dep}' not found.")
            console.print(f"[yellow]💡 Tip:[/yellow] Add the {dep} module first:")
            if dep == "user":
                console.print(f"   [dim]fcube adduser --auth-type email[/dim]")
            else:
                console.print(f"   [dim]fcube startmodule {dep}[/dim]")
            raise typer.Exit(1)
    
    # Generate files using the plugin's self-contained installer to determine actual paths
    try:
        files_to_create = install_plugin(plugin_name, app_dir)
    except Exception as e:
        console.print(f"[bold red]❌ Error:[/bold red] Failed to generate plugin files: {e}")
        raise typer.Exit(1)
    
    # Determine the actual plugin directory from the generated files
    # Some plugins (like deploy_vps) install at project root, not in app/
    if files_to_create:
        first_file_path = files_to_create[0][0]
        # Find the root directory of the plugin by looking for the common parent
        plugin_dir = first_file_path
        while plugin_dir.parent != base_dir and plugin_dir.parent != app_dir:
            plugin_dir = plugin_dir.parent
        # The plugin_dir is the top-level directory of the plugin
        # For deploy-vps, this would be /project/deploy-vps
        # For referral, this would be /project/app/referral
    else:
        plugin_dir = app_dir / plugin_name
    
    # Plugin already exists check
    if plugin_dir.exists() and not force:
        console.print(f"[bold red]❌ Error:[/bold red] Plugin '{plugin_name}' already exists at {plugin_dir}")
        console.print(f"[yellow]💡 Tip:[/yellow] Use --force to overwrite")
        raise typer.Exit(1)
    
    # Process files (dry run or actual installation)
    if dry_run:
        console.print(f"[yellow]🔍 DRY RUN MODE - No files will be created[/yellow]\n")
        console.print(f"[cyan]📋 Preview: Plugin '{plugin_name}' would create:[/cyan]\n")
    else:
        console.print(f"[cyan]📁 Creating {plugin_name} module structure...[/cyan]")
    
    # Dry-run mode: Show preview and exit
    if dry_run:
        # Display files that would be created
        preview_table = Table(
            title=f"📦 Plugin '{plugin_name}' Files Preview",
            show_header=True,
            header_style="bold cyan"
        )
        preview_table.add_column("File Path", style="green")
        preview_table.add_column("Size", style="dim", justify="right")
        preview_table.add_column("Status", style="yellow")
        
        total_size = 0
        for file_path, content in files_to_create:
            relative_path = file_path.relative_to(base_dir)
            size_bytes = len(content.encode('utf-8'))
            total_size += size_bytes
            
            # Format size
            if size_bytes < 1024:
                size_str = f"{size_bytes} B"
            else:
                size_str = f"{size_bytes / 1024:.1f} KB"
            
            # Check if file exists
            status = "Would overwrite" if file_path.exists() else "New file"
            
            preview_table.add_row(str(relative_path), size_str, status)
        
        console.print(preview_table)
        console.print()
        
        # Summary
        summary_table = Table(title=f"📊 Dry Run Summary", show_header=False, box=None)
        summary_table.add_row("[bold]Plugin:[/bold]", f"[cyan]{metadata.name}[/cyan]")
        summary_table.add_row("[bold]Version:[/bold]", f"[cyan]{metadata.version}[/cyan]")
        summary_table.add_row("[bold]Total Files:[/bold]", f"[green]{len(files_to_create)}[/green]")
        summary_table.add_row("[bold]Total Size:[/bold]", f"[green]{total_size / 1024:.1f} KB[/green]")
        summary_table.add_row("[bold]Target Dir:[/bold]", f"[cyan]{plugin_dir}[/cyan]")
        
        console.print(summary_table)
        console.print()
        
        # Post-install preview
        console.print(
            Panel(
                metadata.post_install_notes,
                title="[bold yellow]📝 Post-Install Steps (Preview)[/bold yellow]",
                border_style="yellow",
                padding=(1, 2),
            )
        )
        
        console.print(f"\n[bold yellow]ℹ️  This was a dry run - no files were created.[/bold yellow]")
        console.print(f"[dim]To install for real, run: fcube addplugin {plugin_name}[/dim]\n")
        return
    
    # Actual installation (non-dry-run)
    # Ensure directories exist
    for file_path, _ in files_to_create:
        ensure_directory(file_path.parent)
    
    # Create files
    console.print(f"[cyan]📝 Generating files...[/cyan]\n")
    
    created_files = []
    for file_path, content in files_to_create:
        relative_path = file_path.relative_to(base_dir)
        if write_file(file_path, content, overwrite=force):
            created_files.append(str(relative_path))
            console.print(f"  [green]✓[/green] Created: {relative_path}")
    
    console.print()
    
    # Show directory tree
    tree = Tree(f"[bold cyan]{plugin_name}/[/bold cyan]")
    _build_tree(tree, plugin_dir, plugin_dir)
    console.print(tree)
    console.print()
    
    # Summary
    summary_table = Table(title=f"📊 Plugin '{plugin_name}' Summary", show_header=False, box=None)
    summary_table.add_row("[bold]Plugin:[/bold]", f"[cyan]{metadata.name}[/cyan]")
    summary_table.add_row("[bold]Version:[/bold]", f"[cyan]{metadata.version}[/cyan]")
    summary_table.add_row("[bold]Location:[/bold]", f"[cyan]{plugin_dir}[/cyan]")
    summary_table.add_row("[bold]Files Created:[/bold]", f"[green]{len(created_files)}[/green]")
    summary_table.add_row("[bold]Dependencies:[/bold]", f"[yellow]{', '.join(metadata.dependencies) or 'None'}[/yellow]")
    
    console.print(summary_table)
    console.print()
    
    # Post-install notes
    console.print(
        Panel(
            metadata.post_install_notes,
            title="[bold green]✨ Next Steps[/bold green]",
            border_style="green",
            padding=(1, 2),
        )
    )
    
    console.print(f"\n[bold green]✅ Plugin '{plugin_name}' added successfully![/bold green]\n")


def _build_tree(tree: Tree, current_path: Path, base_path: Path):
    """Recursively build a rich Tree from directory structure."""
    try:
        paths = sorted(current_path.iterdir(), key=lambda p: (not p.is_dir(), p.name))
        for path in paths:
            if path.name.startswith("__pycache__"):
                continue
            if path.is_dir():
                if not any(path.iterdir()):
                    continue
                sub_tree = tree.add(f"[bold blue]{path.name}/[/bold blue]")
                _build_tree(sub_tree, path, base_path)
            else:
                icon = "🐍" if path.suffix == ".py" else "📄"
                tree.add(f"{icon} {path.name}")
    except PermissionError:
        pass
