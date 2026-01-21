"""
List Modules Command - List all existing modules.

Scans the app directory and displays all modules that follow
the modular structure pattern with their components.
"""

from pathlib import Path
from rich.console import Console
from rich.table import Table
from typing import List, Dict, Any

console = Console()


def listmodules_command(directory: str = "app"):
    """
    List all existing modular FastAPI modules.
    """
    console.print(
        f"\n[bold blue]🧊 FCube CLI - Listing modules...[/bold blue]\n"
    )

    base_dir = Path.cwd()
    app_dir = base_dir / directory

    if not app_dir.exists():
        console.print(
            f"[bold red]❌ Error:[/bold red] Directory '{directory}' does not exist",
            style="red"
        )
        return

    # Find all modules
    modules: List[Dict[str, Any]] = []
    
    # Skip these directories (not modules)
    skip_dirs = {"__pycache__", "apis", "core", "scripts"}
    
    for item in app_dir.iterdir():
        if not item.is_dir():
            continue
        if item.name.startswith("_") or item.name.startswith("."):
            continue
        if item.name in skip_dirs:
            continue
        
        # Check if it looks like a module
        has_init = (item / "__init__.py").exists()
        if not has_init:
            continue
        
        # Analyze module structure
        module_info = analyze_module(item)
        if module_info:
            modules.append(module_info)

    if not modules:
        console.print(
            "[yellow]No modules found.[/yellow]"
        )
        console.print(
            "[dim]Use 'fcube startmodule <name>' to create a new module.[/dim]"
        )
        return

    # Display table
    table = Table(title=f"📦 Modules in '{directory}/'")
    table.add_column("Module", style="cyan", no_wrap=True)
    table.add_column("Structure", style="green")
    table.add_column("Models", justify="center")
    table.add_column("Services", justify="center")
    table.add_column("Routes", justify="center")
    table.add_column("Admin", justify="center")
    table.add_column("Public", justify="center")

    for module in sorted(modules, key=lambda x: x["name"]):
        structure = "📁 Modern" if module["is_modern"] else "📄 Flat"
        table.add_row(
            module["name"],
            structure,
            str(module["model_count"]) if module["model_count"] > 0 else "-",
            str(module["service_count"]) if module["service_count"] > 0 else "-",
            str(module["route_count"]) if module["route_count"] > 0 else "-",
            "✓" if module["has_admin"] else "-",
            "✓" if module["has_public"] else "-",
        )

    console.print(table)
    console.print()
    console.print(f"[dim]Total modules: {len(modules)}[/dim]")
    console.print()


def analyze_module(module_path: Path) -> Dict[str, Any]:
    """
    Analyze a module directory and return its structure info.
    """
    module_name = module_path.name
    
    # Check for modern folder structure (models/, schemas/, etc.)
    has_models_folder = (module_path / "models").is_dir()
    has_schemas_folder = (module_path / "schemas").is_dir()
    has_crud_folder = (module_path / "crud").is_dir()
    has_services_folder = (module_path / "services").is_dir()
    has_routes_folder = (module_path / "routes").is_dir()
    
    is_modern = has_models_folder or has_services_folder or has_routes_folder
    
    # Count entities
    model_count = 0
    if has_models_folder:
        model_count = len([
            f for f in (module_path / "models").glob("*.py")
            if not f.name.startswith("_") and f.name != "enums.py"
        ])
    elif (module_path / "models.py").exists():
        model_count = 1
    
    service_count = 0
    if has_services_folder:
        service_count = len([
            f for f in (module_path / "services").glob("*.py")
            if not f.name.startswith("_")
        ])
        # Also count subdirectories (domain folders like review/)
        service_count += len([
            d for d in (module_path / "services").iterdir()
            if d.is_dir() and not d.name.startswith("_")
        ])
    elif (module_path / "services.py").exists():
        service_count = 1
    
    route_count = 0
    if has_routes_folder:
        route_count = len([
            f for f in (module_path / "routes").glob("*.py")
            if not f.name.startswith("_")
        ])
        # Count subdirectories
        for subdir in (module_path / "routes").iterdir():
            if subdir.is_dir() and not subdir.name.startswith("_"):
                route_count += len([
                    f for f in subdir.glob("*.py")
                    if not f.name.startswith("_")
                ])
    elif (module_path / "routes.py").exists():
        route_count = 1
    
    # Check for admin/public routes
    has_admin = (module_path / "routes" / "admin").is_dir()
    has_public = (module_path / "routes" / "public").is_dir()
    
    return {
        "name": module_name,
        "is_modern": is_modern,
        "model_count": model_count,
        "service_count": service_count,
        "route_count": route_count,
        "has_admin": has_admin,
        "has_public": has_public,
    }
