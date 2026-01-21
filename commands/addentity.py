"""
Add Entity Command - Add a new entity to an existing module.

Creates model, schema, and CRUD files for a new entity within
an existing module.
"""

import typer
from pathlib import Path
from rich.console import Console
from typing import List, Tuple

from ..utils.helpers import (
    to_snake_case,
    to_pascal_case,
    ensure_directory,
    write_file,
)
from ..templates import (
    generate_model,
    generate_schemas,
    generate_crud,
)

console = Console()


def addentity_command(
    module_name: str,
    entity_name: str,
    directory: str = "app",
    force: bool = False,
):
    """
    Add a new entity to an existing module.
    """
    console.print(
        f"\n[bold blue]🧊 FCube CLI - Adding new entity...[/bold blue]\n"
    )

    # Convert names
    module_snake = to_snake_case(module_name)
    entity_snake = to_snake_case(entity_name)
    entity_class = to_pascal_case(entity_name)

    # Define paths
    base_dir = Path.cwd()
    module_dir = base_dir / directory / module_snake

    # Check if module exists
    if not module_dir.exists():
        console.print(
            f"[bold red]❌ Error:[/bold red] Module '{module_snake}' does not exist at {module_dir}",
            style="red"
        )
        console.print(
            f"[yellow]💡 Tip:[/yellow] Use 'fcube startmodule {module_name}' to create it first"
        )
        raise typer.Exit(1)

    # Check required folders exist
    required_folders = ["models", "schemas", "crud"]
    for folder in required_folders:
        folder_path = module_dir / folder
        if not folder_path.exists():
            console.print(
                f"[bold red]❌ Error:[/bold red] Module '{module_snake}' is missing '{folder}/' folder",
                style="red"
            )
            console.print(
                f"[yellow]💡 Tip:[/yellow] This module may not follow the FCube structure"
            )
            raise typer.Exit(1)

    # Generate files
    files_to_create: List[Tuple[Path, str]] = [
        (module_dir / "models" / f"{entity_snake}.py", generate_model(entity_snake, entity_class)),
        (module_dir / "schemas" / f"{entity_snake}_schemas.py", generate_schemas(entity_snake, entity_class)),
        (module_dir / "crud" / f"{entity_snake}_crud.py", generate_crud(entity_snake, entity_class)),
    ]

    # Track created files
    created_files = []
    skipped_files = []

    console.print(f"[cyan]📝 Generating files...[/cyan]\n")

    for file_path, content in files_to_create:
        relative_path = file_path.relative_to(module_dir)
        if write_file(file_path, content, overwrite=force):
            created_files.append(str(relative_path))
            console.print(f"  [green]✓[/green] Created: {relative_path}")
        else:
            skipped_files.append(str(relative_path))
            console.print(f"  [yellow]⊘[/yellow] Skipped: {relative_path} (already exists)")

    console.print()

    # Instructions
    instructions = f"""
[bold cyan]Next Steps:[/bold cyan]

1. [bold]Add to model exports[/bold]
   Edit [yellow]{module_snake}/models/__init__.py[/yellow]:
   
   [dim]from .{entity_snake} import {entity_class}[/dim]

2. [bold]Add to schema exports[/bold]
   Edit [yellow]{module_snake}/schemas/__init__.py[/yellow]:
   
   [dim]from .{entity_snake}_schemas import (
       {entity_class}Base,
       {entity_class}Create,
       {entity_class}Update,
       {entity_class} as {entity_class}Response,
   )[/dim]

3. [bold]Add to CRUD exports[/bold]
   Edit [yellow]{module_snake}/crud/__init__.py[/yellow]:
   
   [dim]from .{entity_snake}_crud import {entity_class}CRUD, {entity_snake}_crud[/dim]

4. [bold]Create a service[/bold] (optional)
   Create [yellow]{module_snake}/services/{entity_snake}_service.py[/yellow]

5. [bold]Generate migration[/bold]
   [dim]alembic revision --autogenerate -m "Add {entity_snake} table"
   alembic upgrade head[/dim]
"""

    console.print(instructions)
    console.print(
        f"\n[bold green]✅ Entity '{entity_class}' added to '{module_snake}' successfully![/bold green]\n"
    )
