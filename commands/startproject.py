"""
Start Project Command - Generates a complete FastAPI project.

Creates a new FastAPI project with the following structure:
project_name/
├── app/
│   ├── __init__.py
│   ├── apis/
│   │   ├── __init__.py
│   │   └── v1.py
│   ├── core/
│   │   ├── __init__.py
│   │   ├── alembic_models_import.py
│   │   ├── celery_app.py
│   │   ├── crud.py
│   │   ├── database.py
│   │   ├── exceptions.py
│   │   ├── logging.py
│   │   ├── main.py
│   │   ├── middleware.py
│   │   ├── models.py
│   │   └── settings.py
│   └── user/
│       ├── __init__.py
│       ├── models.py
│       ├── schemas.py
│       ├── crud.py
│       ├── exceptions.py
│       ├── routes.py
│       └── auth_management/
│           ├── __init__.py
│           ├── routes.py
│           ├── service.py
│           └── utils.py
├── migrations/
│   ├── env.py
│   ├── script.py.mako
│   └── versions/
├── docker/
│   ├── Dockerfile
│   ├── docker-entrypoint.sh
│   ├── celery-worker-entrypoint.sh
│   └── flower-entrypoint.sh
├── docker-compose.yml
├── alembic.ini
├── pyproject.toml
├── .env.example
├── .gitignore
├── fcube.py
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
    ensure_directory,
    write_file,
)
from ..templates.project import (
    # Core templates
    generate_core_init,
    generate_core_models,
    generate_core_database,
    generate_core_settings,
    generate_core_crud,
    generate_core_exceptions,
    generate_core_logging,
    generate_core_main,
    generate_core_middleware,
    generate_core_celery,
    generate_core_alembic_models,
    # User templates
    generate_user_init,
    generate_user_models,
    generate_user_schemas,
    generate_user_crud,
    generate_user_exceptions,
    generate_user_routes,
    generate_user_auth_init,
    generate_user_auth_routes,
    generate_user_auth_service,
    generate_user_auth_utils,
    # API templates
    generate_apis_init,
    generate_apis_v1,
    # Project root templates
    generate_docker_compose,
    generate_dockerfile,
    generate_docker_entrypoint,
    generate_celery_entrypoint,
    generate_flower_entrypoint,
    generate_alembic_ini,
    generate_alembic_env,
    generate_alembic_script_mako,
    generate_pyproject_toml,
    generate_env_example,
    generate_gitignore,
    generate_project_readme,
    generate_fcube_script,
)

console = Console()


def startproject_command(
    project_name: str,
    directory: str = ".",
    with_celery: bool = True,
    with_docker: bool = True,
    force: bool = False,
):
    """
    Create a new FastAPI project with complete infrastructure.
    """
    console.print(
        f"\n[bold blue]🧊 FCube CLI - Creating new project...[/bold blue]\n"
    )

    # Convert project name
    project_snake = to_snake_case(project_name)
    project_pascal = to_pascal_case(project_name)

    # Define paths
    base_dir = Path.cwd()
    if directory == ".":
        project_dir = base_dir / project_snake
    else:
        project_dir = base_dir / directory / project_snake

    # Check if directory exists
    if project_dir.exists() and not force:
        console.print(
            f"[bold red]❌ Error:[/bold red] Project '{project_snake}' already exists at {project_dir}",
            style="red"
        )
        console.print(
            f"[yellow]💡 Tip:[/yellow] Use --force flag to overwrite existing files"
        )
        raise typer.Exit(1)

    # Create directory structure
    console.print(f"[cyan]📁 Creating project structure...[/cyan]")
    
    directories_to_create = [
        project_dir,
        project_dir / "app",
        project_dir / "app" / "apis",
        project_dir / "app" / "core",
        project_dir / "app" / "user",
        project_dir / "app" / "user" / "auth_management",
        project_dir / "migrations",
        project_dir / "migrations" / "versions",
        project_dir / "logs",
    ]
    
    if with_docker:
        directories_to_create.append(project_dir / "docker")
    
    for dir_path in directories_to_create:
        ensure_directory(dir_path)

    # Generate files
    files_to_create: List[Tuple[Path, str]] = []
    
    # === App root ===
    files_to_create.append(
        (project_dir / "app" / "__init__.py", "")
    )
    
    # === Core module ===
    files_to_create.extend([
        (project_dir / "app" / "core" / "__init__.py", generate_core_init(project_snake, project_pascal)),
        (project_dir / "app" / "core" / "models.py", generate_core_models()),
        (project_dir / "app" / "core" / "database.py", generate_core_database()),
        (project_dir / "app" / "core" / "settings.py", generate_core_settings(project_snake, project_pascal)),
        (project_dir / "app" / "core" / "crud.py", generate_core_crud()),
        (project_dir / "app" / "core" / "exceptions.py", generate_core_exceptions()),
        (project_dir / "app" / "core" / "logging.py", generate_core_logging()),
        (project_dir / "app" / "core" / "main.py", generate_core_main(project_snake, project_pascal)),
        (project_dir / "app" / "core" / "middleware.py", generate_core_middleware()),
        (project_dir / "app" / "core" / "alembic_models_import.py", generate_core_alembic_models()),
    ])
    
    if with_celery:
        files_to_create.append(
            (project_dir / "app" / "core" / "celery_app.py", generate_core_celery())
        )
    
    # === APIs ===
    files_to_create.extend([
        (project_dir / "app" / "apis" / "__init__.py", generate_apis_init()),
        (project_dir / "app" / "apis" / "v1.py", generate_apis_v1()),
    ])
    
    # === User module ===
    files_to_create.extend([
        (project_dir / "app" / "user" / "__init__.py", generate_user_init()),
        (project_dir / "app" / "user" / "models.py", generate_user_models()),
        (project_dir / "app" / "user" / "schemas.py", generate_user_schemas()),
        (project_dir / "app" / "user" / "crud.py", generate_user_crud()),
        (project_dir / "app" / "user" / "exceptions.py", generate_user_exceptions()),
        (project_dir / "app" / "user" / "routes.py", generate_user_routes()),
        # Auth management
        (project_dir / "app" / "user" / "auth_management" / "__init__.py", generate_user_auth_init()),
        (project_dir / "app" / "user" / "auth_management" / "routes.py", generate_user_auth_routes()),
        (project_dir / "app" / "user" / "auth_management" / "service.py", generate_user_auth_service()),
        (project_dir / "app" / "user" / "auth_management" / "utils.py", generate_user_auth_utils()),
    ])
    
    # === Migrations ===
    files_to_create.extend([
        (project_dir / "alembic.ini", generate_alembic_ini()),
        (project_dir / "migrations" / "env.py", generate_alembic_env()),
        (project_dir / "migrations" / "script.py.mako", generate_alembic_script_mako()),
        (project_dir / "migrations" / "README", "Generic single-database configuration with async support."),
    ])
    
    # === Docker ===
    if with_docker:
        files_to_create.extend([
            (project_dir / "docker-compose.yml", generate_docker_compose(project_snake, with_celery)),
            (project_dir / "docker" / "Dockerfile", generate_dockerfile()),
            (project_dir / "docker" / "docker-entrypoint.sh", generate_docker_entrypoint()),
        ])
        if with_celery:
            files_to_create.extend([
                (project_dir / "docker" / "celery-worker-entrypoint.sh", generate_celery_entrypoint()),
                (project_dir / "docker" / "flower-entrypoint.sh", generate_flower_entrypoint()),
            ])
    
    # === Project root files ===
    files_to_create.extend([
        (project_dir / "pyproject.toml", generate_pyproject_toml(project_snake, with_celery)),
        (project_dir / ".env.example", generate_env_example(project_snake, with_celery)),
        (project_dir / ".gitignore", generate_gitignore()),
        (project_dir / "README.md", generate_project_readme(project_snake, project_pascal, with_celery, with_docker)),
        (project_dir / "fcube.py", generate_fcube_script()),
    ])

    # Track created files
    created_files = []
    skipped_files = []

    # Create files
    console.print(f"[cyan]📝 Generating files...[/cyan]\n")

    for file_path, content in files_to_create:
        relative_path = file_path.relative_to(project_dir)
        if write_file(file_path, content, overwrite=force):
            created_files.append(str(relative_path))
            console.print(f"  [green]✓[/green] Created: {relative_path}")
        else:
            skipped_files.append(str(relative_path))
            console.print(f"  [yellow]⊘[/yellow] Skipped: {relative_path}")

    # Show directory tree
    console.print()
    tree = Tree(f"[bold cyan]{project_snake}/[/bold cyan]")
    _build_tree(tree, project_dir, project_dir)
    console.print(tree)
    console.print()

    # Summary
    summary_table = Table(title="📊 Project Summary", show_header=False, box=None)
    summary_table.add_row("[bold]Project Name:[/bold]", f"[cyan]{project_pascal}[/cyan]")
    summary_table.add_row("[bold]Project Path:[/bold]", f"[cyan]{project_snake}[/cyan]")
    summary_table.add_row("[bold]Location:[/bold]", f"[cyan]{project_dir}[/cyan]")
    summary_table.add_row("[bold]Files Created:[/bold]", f"[green]{len(created_files)}[/green]")
    summary_table.add_row("[bold]Docker:[/bold]", f"[{'green' if with_docker else 'yellow'}]{'Yes' if with_docker else 'No'}[/]")
    summary_table.add_row("[bold]Celery:[/bold]", f"[{'green' if with_celery else 'yellow'}]{'Yes' if with_celery else 'No'}[/]")

    if skipped_files:
        summary_table.add_row("[bold]Files Skipped:[/bold]", f"[yellow]{len(skipped_files)}[/yellow]")

    console.print(summary_table)
    console.print()

    # Next steps panel
    next_steps = f"""
[bold cyan]1. Navigate to project[/bold cyan]
   [dim]cd {project_snake}[/dim]

[bold cyan]2. Set up environment[/bold cyan]
   [dim]cp .env.example .env
   # Edit .env with your configuration[/dim]

[bold cyan]3. Install dependencies[/bold cyan]
   [dim]pip install uv  # If not installed
   uv pip install -r pyproject.toml[/dim]

[bold cyan]4. Start services with Docker (recommended)[/bold cyan]
   [dim]docker-compose up -d postgres redis
   # Wait for services to be healthy[/dim]

[bold cyan]5. Run migrations[/bold cyan]
   [dim]alembic revision --autogenerate -m "Initial migration"
   alembic upgrade head[/dim]

[bold cyan]6. Start the application[/bold cyan]
   [dim]# With Docker:
   docker-compose up -d
   
   # Or locally:
   uvicorn app.core.main:app --reload[/dim]

[bold cyan]7. Access your API[/bold cyan]
   [dim]API Docs: http://localhost:8000/docs
   Health:   http://localhost:8000/health[/dim]

[bold cyan]8. Create new modules[/bold cyan]
   [dim]python fcube.py startmodule Product[/dim]
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
        f"\n[bold green]✅ Project '{project_pascal}' created successfully![/bold green]\n"
    )


def _build_tree(tree: Tree, current_path: Path, base_path: Path):
    """Recursively build a rich Tree from directory structure."""
    try:
        paths = sorted(current_path.iterdir(), key=lambda p: (not p.is_dir(), p.name))
        for path in paths:
            if path.name.startswith("__pycache__"):
                continue
            if path.name == ".git":
                continue
            if path.is_dir():
                # Skip empty directories
                if not any(path.iterdir()):
                    continue
                sub_tree = tree.add(f"[bold blue]{path.name}/[/bold blue]")
                _build_tree(sub_tree, path, base_path)
            else:
                icon = "📄" if path.suffix == ".md" else "🐍" if path.suffix == ".py" else "🐳" if path.name.startswith("docker") or path.name == "Dockerfile" else "⚙️" if path.suffix in [".toml", ".ini", ".yml", ".yaml"] else "📁"
                tree.add(f"{icon} {path.name}")
    except PermissionError:
        pass
