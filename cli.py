"""
FCube CLI - Main CLI Application

The main Typer application for FCube - a FastAPI project and module generator
that follows the industry-standard architecture patterns.

Commands:
- startproject: Create a new FastAPI project with core module (no user by default)
- adduser: Add user module with configurable authentication (email, phone, both)
- addplugin: Add pre-built plugin modules (referral, notifications, etc.)
- startmodule: Create a new module with complete folder structure
- addentity: Add a new entity to an existing module
- listmodules: List all existing modules
- version: Show CLI version
"""

import typer
from rich.console import Console
from typing import Optional

from .commands.startproject import startproject_command
from .commands.startmodule import startmodule_command
from .commands.addentity import addentity_command
from .commands.adduser import adduser_command, AuthType
from .commands.addplugin import addplugin_command
from .commands.listmodules import listmodules_command

# Initialize Typer app
app = typer.Typer(
    name="fcube",
    help="🧊 FCube CLI - Modern FastAPI Project & Module Generator",
    add_completion=True,
    rich_markup_mode="rich",
)

console = Console()


@app.command("startproject")
def startproject(
    project_name: str = typer.Argument(..., help="Name of the project to create"),
    directory: str = typer.Option(
        ".",
        "--dir",
        "-d",
        help="Directory where the project will be created"
    ),
    with_celery: bool = typer.Option(
        True,
        "--celery/--no-celery",
        help="Include Celery for background tasks"
    ),
    with_docker: bool = typer.Option(
        True,
        "--docker/--no-docker",
        help="Include Docker configuration"
    ),
    force: bool = typer.Option(
        False,
        "--force",
        "-f",
        help="Overwrite existing files"
    ),
):
    """
    🚀 Create a new FastAPI project with complete infrastructure.

    This command generates a production-ready FastAPI project including:

    • Core module (database, settings, logging, exceptions)
    • Docker & docker-compose configuration
    • Alembic migrations setup
    • Celery for background tasks
    • Redis for caching
    • PostgreSQL database

    NOTE: User module is NOT created by default.
    Use 'fcube adduser' to add authentication.

    [bold cyan]Examples:[/bold cyan]

      $ python fcube.py startproject MyProject

      $ python fcube.py startproject api-backend --dir projects

      $ python fcube.py startproject simple-api --no-celery --no-docker
    """
    startproject_command(
        project_name=project_name,
        directory=directory,
        with_celery=with_celery,
        with_docker=with_docker,
        force=force
    )


@app.command("adduser")
def adduser(
    directory: str = typer.Option(
        "app",
        "--dir",
        "-d",
        help="Directory where the user module will be created"
    ),
    auth_type: AuthType = typer.Option(
        AuthType.EMAIL,
        "--auth-type",
        "-a",
        help="Authentication type: email, phone, or both"
    ),
    force: bool = typer.Option(
        False,
        "--force",
        "-f",
        help="Overwrite existing files"
    ),
):
    """
    👤 Add user module with configurable authentication.

    Creates a complete user module with authentication system.
    Choose from different authentication strategies:

    • email: Email + Password with JWT tokens
    • phone: Phone + OTP with SMS verification
    • both: Combined email and phone authentication

    [bold cyan]Examples:[/bold cyan]

      $ python fcube.py adduser --auth-type email

      $ python fcube.py adduser --auth-type phone

      $ python fcube.py adduser --auth-type both

      $ python fcube.py adduser -a email --force
    """
    adduser_command(
        directory=directory,
        auth_type=auth_type,
        force=force
    )


@app.command("addplugin")
def addplugin(
    plugin_name: str = typer.Argument(
        None,
        help="Name of the plugin to add (e.g., referral)"
    ),
    directory: str = typer.Option(
        "app",
        "--dir",
        "-d",
        help="Directory where the plugin will be created"
    ),
    force: bool = typer.Option(
        False,
        "--force",
        "-f",
        help="Overwrite existing files"
    ),
    list_plugins: bool = typer.Option(
        False,
        "--list",
        "-l",
        help="List all available plugins"
    ),
):
    """
    🔌 Add a pre-built plugin module to your project.

    Plugins are self-contained feature modules that can be added
    to any FCube-generated project. Available plugins:

    • referral: User referral system with completion strategies
    • (more coming soon...)

    [bold cyan]Examples:[/bold cyan]

      $ python fcube.py addplugin --list

      $ python fcube.py addplugin referral

      $ python fcube.py addplugin referral --force
    """
    addplugin_command(
        plugin_name=plugin_name,
        directory=directory,
        force=force,
        list_plugins=list_plugins
    )


@app.command("startmodule")
def startmodule(
    module_name: str = typer.Argument(..., help="Name of the module to create"),
    directory: str = typer.Option(
        "app",
        "--dir",
        "-d",
        help="Directory where the module will be created"
    ),
    with_admin: bool = typer.Option(
        True,
        "--admin/--no-admin",
        help="Include admin routes with permissions"
    ),
    with_public: bool = typer.Option(
        True,
        "--public/--no-public",
        help="Include public routes (no auth required)"
    ),
    force: bool = typer.Option(
        False,
        "--force",
        "-f",
        help="Overwrite existing files"
    ),
):
    """
    Create a new modular FastAPI module with complete folder structure.

    This command generates a production-ready module following the Korab Backend
    architecture patterns including:

    • Layered Architecture (Models → Schemas → CRUD → Services → Routes)
    • Dependency Injection with singleton services
    • Role-based route organization (public/, admin/)
    • Permission-based access control
    • HTTPException-based error handling
    • Transaction management (Service layer owns commits)
    • Integration facades for cross-module communication

    [bold cyan]Examples:[/bold cyan]

      $ python fcube.py startmodule product

      $ python fcube.py startmodule inventory --dir app

      $ python fcube.py startmodule order --no-admin --force
    """
    startmodule_command(
        module_name=module_name,
        directory=directory,
        with_admin=with_admin,
        with_public=with_public,
        force=force
    )


@app.command("addentity")
def addentity(
    module_name: str = typer.Argument(..., help="Name of the existing module"),
    entity_name: str = typer.Argument(..., help="Name of the entity to add"),
    directory: str = typer.Option(
        "app",
        "--dir",
        "-d",
        help="Directory where modules are located"
    ),
    force: bool = typer.Option(
        False,
        "--force",
        "-f",
        help="Overwrite existing files"
    ),
):
    """
    Add a new entity to an existing module.

    Creates model, schema, and CRUD files for a new entity within
    an existing module.

    [bold cyan]Examples:[/bold cyan]

      $ python fcube.py addentity service_provider availability

      $ python fcube.py addentity booking payment --force
    """
    addentity_command(
        module_name=module_name,
        entity_name=entity_name,
        directory=directory,
        force=force
    )


@app.command("listmodules")
def listmodules(
    directory: str = typer.Option(
        "app",
        "--dir",
        "-d",
        help="Directory to scan for modules"
    ),
):
    """
    List all existing modular FastAPI modules.

    Scans the app directory and displays all modules that follow
    the modular structure pattern with their components.

    [bold cyan]Examples:[/bold cyan]

      $ python fcube.py listmodules

      $ python fcube.py listmodules --dir app
    """
    listmodules_command(directory)


@app.command("version")
def version():
    """how FCube CLI version."""
    from . import __version__
    console.print(
        f"[bold cyan] FCube CLI[/bold cyan] version [green]{__version__}[/green]"
    )


@app.callback(invoke_without_command=True)
def main(
    ctx: typer.Context,
    version: Optional[bool] = typer.Option(
        None,
        "--version",
        "-v",
        help="Show version and exit",
        is_flag=True,
    ),
):
    """
    FCube CLI - Modern FastAPI Module Generator

    A powerful code generation tool for creating production-ready
    FastAPI modules following clean architecture principles.

    [bold]Architecture Features:[/bold]
    • Layered Design (Models → CRUD → Services → Routes)
    • Dependency Injection with @lru_cache singletons
    • Role-based routes (public/, admin/)
    • Permission-based access control
    • Integration facades for cross-module communication
    """
    if version:
        from . import __version__
        console.print(
            f"[bold cyan] FCube CLI[/bold cyan] version [green]{__version__}[/green]"
        )
        raise typer.Exit()

    if ctx.invoked_subcommand is None:
        console.print(ctx.get_help())


# Entry point for running the CLI
if __name__ == "__main__":
    app()
