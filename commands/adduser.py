"""
Add User Command - Adds user module with configurable authentication.

Supports different authentication strategies:
- email: Email + Password authentication (JWT tokens)
- phone: Phone + OTP authentication (SMS verification)
- both: Combined email and phone authentication

Creates the user module structure:
app/user/
├── __init__.py
├── models.py
├── schemas.py
├── crud.py
├── exceptions.py
├── routes.py
├── auth_management/
│   ├── __init__.py
│   ├── routes.py
│   ├── service.py
│   └── utils.py
└── permission_management/
    ├── __init__.py
    ├── utils.py
    └── scoped_access.py
"""

import typer
from pathlib import Path
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from typing import List, Tuple

from ..utils.helpers import (
    ensure_directory,
    write_file,
)
from ..templates.project.user import (
    AuthType,
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
    generate_user_permission_init,
    generate_user_permission_utils,
    generate_user_permission_scoped_access,
)
from ..templates.project.api_templates import generate_apis_v1


console = Console()


def adduser_command(
    directory: str = "app",
    auth_type: AuthType = AuthType.EMAIL,
    force: bool = False,
):
    """
    Add user module with configurable authentication.
    """
    console.print(f"\n[bold blue]🧊 FCube CLI - Adding User Module...[/bold blue]\n")
    console.print(f"[cyan]Authentication Type:[/cyan] [bold]{auth_type.value}[/bold]\n")
    
    # Define paths
    base_dir = Path.cwd()
    app_dir = base_dir / directory
    user_dir = app_dir / "user"
    
    # Check if app directory exists
    if not app_dir.exists():
        console.print(f"[bold red]❌ Error:[/bold red] Directory '{directory}' not found.")
        console.print(f"[yellow]💡 Tip:[/yellow] Make sure you're in the project root directory.")
        raise typer.Exit(1)
    
    # Check if user module already exists
    if user_dir.exists() and not force:
        console.print(f"[bold red]❌ Error:[/bold red] User module already exists at {user_dir}")
        console.print(f"[yellow]💡 Tip:[/yellow] Use --force to overwrite existing files")
        raise typer.Exit(1)
    
    # Create directories
    console.print(f"[cyan]📁 Creating user module structure...[/cyan]")
    
    directories = [
        user_dir,
        user_dir / "auth_management",
        user_dir / "permission_management",
    ]
    
    for dir_path in directories:
        ensure_directory(dir_path)
    
    # Generate files using templates
    files_to_create: List[Tuple[Path, str]] = [
        # User module root files
        (user_dir / "__init__.py", generate_user_init()),
        (user_dir / "models.py", generate_user_models(auth_type)),
        (user_dir / "schemas.py", generate_user_schemas(auth_type)),
        (user_dir / "crud.py", generate_user_crud()),
        (user_dir / "exceptions.py", generate_user_exceptions()),
        (user_dir / "routes.py", generate_user_routes()),
        # Auth management
        (user_dir / "auth_management" / "__init__.py", generate_user_auth_init()),
        (user_dir / "auth_management" / "routes.py", generate_user_auth_routes()),
        (user_dir / "auth_management" / "service.py", generate_user_auth_service()),
        (user_dir / "auth_management" / "utils.py", generate_user_auth_utils()),
        # Permission management
        (user_dir / "permission_management" / "__init__.py", generate_user_permission_init()),
        (user_dir / "permission_management" / "utils.py", generate_user_permission_utils()),
        (user_dir / "permission_management" / "scoped_access.py", generate_user_permission_scoped_access()),
    ]
    
    # Create files
    console.print(f"[cyan]📝 Generating files...[/cyan]\n")
    
    created_files = []
    for file_path, content in files_to_create:
        relative_path = file_path.relative_to(base_dir)
        if write_file(file_path, content, overwrite=force):
            created_files.append(str(relative_path))
            console.print(f"  [green]✓[/green] Created: {relative_path}")
    
    # Update apis/v1.py
    v1_path = app_dir / "apis" / "v1.py"
    if v1_path.exists():
        write_file(v1_path, generate_apis_v1(), overwrite=True)
        console.print(f"  [green]✓[/green] Updated: {v1_path.relative_to(base_dir)}")
    
    # Summary
    console.print()
    
    summary_table = Table(title="📊 User Module Summary", show_header=False, box=None)
    summary_table.add_row("[bold]Auth Type:[/bold]", f"[cyan]{auth_type.value}[/cyan]")
    summary_table.add_row("[bold]Location:[/bold]", f"[cyan]{user_dir}[/cyan]")
    summary_table.add_row("[bold]Files Created:[/bold]", f"[green]{len(created_files)}[/green]")
    
    if auth_type == AuthType.EMAIL:
        summary_table.add_row("[bold]Features:[/bold]", "Email + Password, JWT tokens")
    elif auth_type == AuthType.PHONE:
        summary_table.add_row("[bold]Features:[/bold]", "Phone + OTP, SMS verification")
    else:
        summary_table.add_row("[bold]Features:[/bold]", "Email + Password, Phone + OTP")
    
    console.print(summary_table)
    console.print()
    
    # Next steps
    next_steps = f"""
[bold cyan]1. Update alembic_models_import.py[/bold cyan]
   [dim]Add: from app.user.models import User, Role, Permission[/dim]

[bold cyan]2. Generate migration[/bold cyan]
   [dim]alembic revision --autogenerate -m "Add user module"
   alembic upgrade head[/dim]

[bold cyan]3. API Endpoints[/bold cyan]
   [dim]POST /api/v1/auth/register - Register user
   POST /api/v1/auth/login - Login user
   GET  /api/v1/auth/me - Get current user[/dim]
"""
    if auth_type in [AuthType.PHONE, AuthType.BOTH]:
        next_steps += """
[bold cyan]4. Configure SMS Provider[/bold cyan]
   [dim]Add SMS_API_KEY, SMS_SENDER_ID to .env
   Implement SMS service in auth_management/sms.py[/dim]
"""
    
    console.print(Panel(next_steps, title="[bold green]✨ Next Steps[/bold green]", border_style="green"))
    console.print(f"\n[bold green]✅ User module added successfully![/bold green]\n")
