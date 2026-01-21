"""
Start Module Command - Generates a new modular FastAPI module.

Creates a complete module with the following structure:
app/{module_name}/
├── __init__.py
├── dependencies.py
├── exceptions.py
├── permissions.py
├── tasks.py
├── models/
│   ├── __init__.py
│   └── {entity}.py
├── schemas/
│   ├── __init__.py
│   └── {entity}_schemas.py
├── crud/
│   ├── __init__.py
│   └── {entity}_crud.py
├── services/
│   ├── __init__.py
│   └── {entity}_service.py
├── routes/
│   ├── __init__.py
│   ├── public/
│   │   ├── __init__.py
│   │   └── {entity}.py
│   └── admin/
│       ├── __init__.py
│       └── {entity}_management.py
├── utils/
│   └── __init__.py
├── integrations/
│   └── __init__.py
└── README.md
"""

import typer
from pathlib import Path
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.tree import Tree
from typing import List, Tuple

from ..utils.helpers import (
    to_snake_case,
    to_pascal_case,
    to_kebab_case,
    ensure_directory,
    write_file,
)
from ..templates import (
    generate_model,
    generate_model_init,
    generate_schemas,
    generate_schema_init,
    generate_crud,
    generate_crud_init,
    generate_service,
    generate_service_init,
    generate_routes_init,
    generate_public_routes,
    generate_public_routes_init,
    generate_admin_routes,
    generate_admin_routes_init,
    generate_dependencies,
    generate_permissions,
    generate_exceptions,
    generate_module_init,
    generate_utils_init,
    generate_integrations_init,
    generate_tasks,
    generate_readme,
)

console = Console()


def startmodule_command(
    module_name: str,
    directory: str = "app",
    with_admin: bool = True,
    with_public: bool = True,
    force: bool = False,
):
    """
    Create a new modular FastAPI module with complete folder structure.
    """
    console.print(
        f"\n[bold blue]🧊 FCube CLI - Creating new module...[/bold blue]\n"
    )

    # Convert module name to different cases
    module_snake = to_snake_case(module_name)
    class_name = to_pascal_case(module_name)
    module_kebab = to_kebab_case(module_name)

    # Define paths
    base_dir = Path.cwd()
    module_dir = base_dir / directory / module_snake

    # Check if directory exists
    if module_dir.exists() and not force:
        console.print(
            f"[bold red]❌ Error:[/bold red] Module '{module_snake}' already exists at {module_dir}",
            style="red"
        )
        console.print(
            f"[yellow]💡 Tip:[/yellow] Use --force flag to overwrite existing files"
        )
        raise typer.Exit(1)

    # Create directory structure
    console.print(f"[cyan]📁 Creating directory structure...[/cyan]")
    
    directories_to_create = [
        module_dir,
        module_dir / "models",
        module_dir / "schemas",
        module_dir / "crud",
        module_dir / "services",
        module_dir / "routes",
        module_dir / "utils",
        module_dir / "integrations",
    ]
    
    if with_public:
        directories_to_create.append(module_dir / "routes" / "public")
    if with_admin:
        directories_to_create.append(module_dir / "routes" / "admin")
    
    for dir_path in directories_to_create:
        ensure_directory(dir_path)

    # Generate files
    files_to_create: List[Tuple[Path, str]] = []
    
    # Root module files
    files_to_create.extend([
        (module_dir / "__init__.py", generate_module_init(module_snake, class_name)),
        (module_dir / "dependencies.py", generate_dependencies(module_snake, class_name)),
        (module_dir / "exceptions.py", generate_exceptions(module_snake, class_name)),
        (module_dir / "permissions.py", generate_permissions(module_snake, class_name)),
        (module_dir / "tasks.py", generate_tasks(module_snake, class_name)),
        (module_dir / "README.md", generate_readme(module_snake, class_name, module_kebab)),
    ])
    
    # Models folder
    files_to_create.extend([
        (module_dir / "models" / "__init__.py", generate_model_init(module_snake, class_name)),
        (module_dir / "models" / f"{module_snake}.py", generate_model(module_snake, class_name)),
    ])
    
    # Schemas folder
    files_to_create.extend([
        (module_dir / "schemas" / "__init__.py", generate_schema_init(module_snake, class_name)),
        (module_dir / "schemas" / f"{module_snake}_schemas.py", generate_schemas(module_snake, class_name)),
    ])
    
    # CRUD folder
    files_to_create.extend([
        (module_dir / "crud" / "__init__.py", generate_crud_init(module_snake, class_name)),
        (module_dir / "crud" / f"{module_snake}_crud.py", generate_crud(module_snake, class_name)),
    ])
    
    # Services folder
    files_to_create.extend([
        (module_dir / "services" / "__init__.py", generate_service_init(module_snake, class_name)),
        (module_dir / "services" / f"{module_snake}_service.py", generate_service(module_snake, class_name)),
    ])
    
    # Routes folder
    files_to_create.append(
        (module_dir / "routes" / "__init__.py", generate_routes_init(module_snake, class_name, with_public, with_admin))
    )
    
    if with_public:
        files_to_create.extend([
            (module_dir / "routes" / "public" / "__init__.py", generate_public_routes_init(module_snake, class_name)),
            (module_dir / "routes" / "public" / f"{module_snake}.py", generate_public_routes(module_snake, class_name)),
        ])
    
    if with_admin:
        files_to_create.extend([
            (module_dir / "routes" / "admin" / "__init__.py", generate_admin_routes_init(module_snake, class_name)),
            (module_dir / "routes" / "admin" / f"{module_snake}_management.py", generate_admin_routes(module_snake, class_name)),
        ])
    
    # Utils folder
    files_to_create.append(
        (module_dir / "utils" / "__init__.py", generate_utils_init(module_snake, class_name))
    )
    
    # Integrations folder
    files_to_create.append(
        (module_dir / "integrations" / "__init__.py", generate_integrations_init(module_snake, class_name))
    )

    # Track created files
    created_files = []
    skipped_files = []

    # Create files
    console.print(f"[cyan]📝 Generating files...[/cyan]\n")

    for file_path, content in files_to_create:
        relative_path = file_path.relative_to(module_dir)
        if write_file(file_path, content, overwrite=force):
            created_files.append(str(relative_path))
            console.print(f"  [green]✓[/green] Created: {relative_path}")
        else:
            skipped_files.append(str(relative_path))
            console.print(f"  [yellow]⊘[/yellow] Skipped: {relative_path} (already exists)")

    # Show directory tree
    console.print()
    tree = Tree(f"[bold cyan]{module_snake}/[/bold cyan]")
    _build_tree(tree, module_dir, module_dir)
    console.print(tree)
    console.print()

    # Summary
    summary_table = Table(title="📊 Summary", show_header=False, box=None)
    summary_table.add_row("[bold]Module Name:[/bold]", f"[cyan]{class_name}[/cyan]")
    summary_table.add_row("[bold]Module Path:[/bold]", f"[cyan]{module_snake}[/cyan]")
    summary_table.add_row("[bold]Location:[/bold]", f"[cyan]{module_dir}[/cyan]")
    summary_table.add_row("[bold]Files Created:[/bold]", f"[green]{len(created_files)}[/green]")
    summary_table.add_row("[bold]Public Routes:[/bold]", f"[{'green' if with_public else 'yellow'}]{'Yes' if with_public else 'No'}[/]")
    summary_table.add_row("[bold]Admin Routes:[/bold]", f"[{'green' if with_admin else 'yellow'}]{'Yes' if with_admin else 'No'}[/]")

    if skipped_files:
        summary_table.add_row("[bold]Files Skipped:[/bold]", f"[yellow]{len(skipped_files)}[/yellow]")

    console.print(summary_table)
    console.print()

    # Next steps panel
    next_steps = f"""
[bold cyan]1. Register the router[/bold cyan]
   Add to [yellow]app/apis/v1.py[/yellow]:
   
   [dim]from app.{module_snake}.routes import {module_snake}_router
   router.include_router({module_snake}_router)[/dim]

[bold cyan]2. Import model for Alembic[/bold cyan]
   Add to [yellow]app/core/alembic_models_import.py[/yellow]:
   
   [dim]from app.{module_snake}.models import {class_name}[/dim]

[bold cyan]3. Generate database migration[/bold cyan]
   
   [dim]alembic revision --autogenerate -m "Add {module_snake} table"
   alembic upgrade head[/dim]

[bold cyan]4. Test your API[/bold cyan]
   
   [dim]uvicorn app.core.main:app --reload[/dim]
   
   Visit: [link]http://localhost:8000/docs[/link]

[bold cyan]5. Customize[/bold cyan]
   
   • Edit [yellow]{module_snake}/models/{module_snake}.py[/yellow] to add fields
   • Update [yellow]{module_snake}/services/{module_snake}_service.py[/yellow] for business logic
   • Modify [yellow]{module_snake}/routes/[/yellow] for custom endpoints
   • Add permissions in [yellow]{module_snake}/permissions.py[/yellow]
"""

    console.print(
        Panel(
            next_steps,
            title="[bold green]✨ Next Steps[/bold green]",
            border_style="green",
            padding=(1, 2),
        )
    )

    console.print(
        f"\n[bold green]✅ Module '{class_name}' created successfully![/bold green]\n"
    )


def _build_tree(tree: Tree, current_path: Path, base_path: Path):
    """Recursively build a rich Tree from directory structure."""
    try:
        paths = sorted(current_path.iterdir(), key=lambda p: (not p.is_dir(), p.name))
        for path in paths:
            if path.name.startswith("__pycache__"):
                continue
            if path.is_dir():
                sub_tree = tree.add(f"[bold blue]{path.name}/[/bold blue]")
                _build_tree(sub_tree, path, base_path)
            else:
                icon = "📄" if path.suffix == ".md" else "🐍" if path.suffix == ".py" else "📁"
                tree.add(f"{icon} {path.name}")
    except PermissionError:
        pass
