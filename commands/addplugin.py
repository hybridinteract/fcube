"""
Add Plugin Command - Universal command for adding plugin modules.

Discovers and installs pre-built plugin modules like:
- referral: User referral system with completion strategies
- (future) notifications: Push/email notification system
- (future) audit: Audit logging system

Usage:
    fcube addplugin referral
    fcube addplugin --list  # Show available plugins
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


def install_referral_plugin(
    app_dir: Path,
    force: bool = False
) -> List[Tuple[Path, str]]:
    """Generate files for the referral plugin."""
    from ..templates.plugins.referral import (
        generate_referral_models,
        generate_referral_config,
        generate_referral_strategies,
        generate_referral_exceptions,
        generate_referral_dependencies,
        generate_referral_tasks,
        generate_referral_schemas,
        generate_referral_schemas_init,
        generate_referral_crud,
        generate_referral_crud_init,
        generate_referral_service,
        generate_referral_service_init,
        generate_referral_routes,
        generate_referral_admin_routes,
        generate_referral_routes_init,
    )
    from ..templates.plugins.referral.model_templates import generate_referral_init
    
    referral_dir = app_dir / "referral"
    
    # Create directories
    directories = [
        referral_dir,
        referral_dir / "schemas",
        referral_dir / "crud",
        referral_dir / "services",
        referral_dir / "routes",
    ]
    
    for dir_path in directories:
        ensure_directory(dir_path)
    
    # Generate files
    files: List[Tuple[Path, str]] = [
        # Root files
        (referral_dir / "__init__.py", generate_referral_init()),
        (referral_dir / "models.py", generate_referral_models()),
        (referral_dir / "config.py", generate_referral_config()),
        (referral_dir / "strategies.py", generate_referral_strategies()),
        (referral_dir / "exceptions.py", generate_referral_exceptions()),
        (referral_dir / "dependencies.py", generate_referral_dependencies()),
        (referral_dir / "tasks.py", generate_referral_tasks()),
        # Schemas
        (referral_dir / "schemas" / "__init__.py", generate_referral_schemas_init()),
        (referral_dir / "schemas" / "referral_schemas.py", generate_referral_schemas()),
        # CRUD
        (referral_dir / "crud" / "__init__.py", generate_referral_crud_init()),
        (referral_dir / "crud" / "referral_crud.py", generate_referral_crud()),
        # Services
        (referral_dir / "services" / "__init__.py", generate_referral_service_init()),
        (referral_dir / "services" / "referral_service.py", generate_referral_service()),
        # Routes
        (referral_dir / "routes" / "__init__.py", generate_referral_routes_init()),
        (referral_dir / "routes" / "referral_routes.py", generate_referral_routes()),
        (referral_dir / "routes" / "referral_admin_routes.py", generate_referral_admin_routes()),
    ]
    
    return files


def addplugin_command(
    plugin_name: str = None,
    directory: str = "app",
    force: bool = False,
    list_plugins: bool = False,
):
    """
    Add a plugin module to your project.
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
    
    # Plugin already exists check
    plugin_dir = app_dir / plugin_name
    if plugin_dir.exists() and not force:
        console.print(f"[bold red]❌ Error:[/bold red] Plugin '{plugin_name}' already exists at {plugin_dir}")
        console.print(f"[yellow]💡 Tip:[/yellow] Use --force to overwrite")
        raise typer.Exit(1)
    
    # Generate files based on plugin
    console.print(f"[cyan]📁 Creating {plugin_name} module structure...[/cyan]")
    
    if plugin_name == "referral":
        files_to_create = install_referral_plugin(app_dir, force)
    else:
        console.print(f"[bold red]❌ Error:[/bold red] Plugin installer for '{plugin_name}' not implemented.")
        raise typer.Exit(1)
    
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
