# FCube CLI

A modular monolith generator for FastAPI applications.

---

## What is FCube?

**FCube** is a CLI tool that generates production-ready FastAPI projects with:

- **Modular architecture** — Clean separation of concerns
- **Dependency injection** — Testable, maintainable code
- **Database patterns** — CRUD, transactions, migrations
- **Plugin system** — Extend with reusable components

```bash
# Create a new project
fcube startproject myapp

# Add a module
fcube addmodule products

# Add authentication
fcube adduser --jwt

# Add a plugin
fcube addplugin referral
```

---

## Why FCube?

### The Problem

Starting a new FastAPI project means:

1. Setting up project structure manually
2. Configuring database connections
3. Implementing auth from scratch
4. Building common patterns repeatedly

This takes **hours** and often leads to inconsistent architectures across projects.

### The Solution

FCube codifies our best practices into a generator:

| Without FCube | With FCube |
|---------------|------------|
| 4+ hours of setup | 2 minutes |
| Inconsistent structure | Standardized architecture |
| Auth from scratch | Built-in JWT + role-based |
| Manual CRUD | Generated CRUD patterns |
| No plugin system | Extensible plugins |

---

## Key Features

<div class="grid cards" markdown>

-   :material-cube-outline:{ .lg .middle } __Modular Architecture__

    ---

    Each module is self-contained with its own models, schemas, CRUD, services, and routes.

-   :material-needle:{ .lg .middle } __Dependency Injection__

    ---

    Clean DI pattern with FastAPI's `Depends()` system for testability.

-   :material-database:{ .lg .middle } __Database Patterns__

    ---

    SQLAlchemy 2.0 ORM, async sessions, and Alembic migrations.

-   :material-shield-check:{ .lg .middle } __Authentication__

    ---

    JWT-based auth with role-based permissions and refresh tokens.

-   :material-puzzle:{ .lg .middle } __Plugin System__

    ---

    Add pre-built features like referral systems or deployment configs.

-   :material-file-code:{ .lg .middle } __Code Generation__

    ---

    Templates for models, schemas, CRUD, services, and routes.

</div>

---

## Quick Start

```bash
# Install FCube
pip install fcube

# Create a new project
fcube startproject myapp
cd myapp

# Set up environment
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Initialize database
alembic upgrade head

# Run the server
uvicorn app.main:app --reload
```

**That's it!** Open [http://localhost:8000/docs](http://localhost:8000/docs) to see your API.

---

## Documentation

<div class="grid cards" markdown>

-   :octicons-rocket-24:{ .lg .middle } __Getting Started__

    ---

    Installation, first project, and basic usage.

    [:octicons-arrow-right-24: Get started](getting-started.md)

-   :octicons-command-palette-24:{ .lg .middle } __Commands Reference__

    ---

    All CLI commands with options and examples.

    [:octicons-arrow-right-24: View commands](commands.md)

-   :octicons-file-directory-24:{ .lg .middle } __Generated Architecture__

    ---

    Understand the project structure and patterns.

    [:octicons-arrow-right-24: Learn architecture](architecture.md)

-   :octicons-plug-24:{ .lg .middle } __Plugin System__

    ---

    Use and create plugins for FCube.

    [:octicons-arrow-right-24: Explore plugins](plugins.md)

-   :octicons-git-pull-request-24:{ .lg .middle } __Contributing__

    ---

    How to contribute to FCube development.

    [:octicons-arrow-right-24: Contribute](contributing.md)

</div>
