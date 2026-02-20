# 🧊 FCube CLI

!!! warning "Under Development"
    The FCube CLI is currently under active development. Please do not use it for production projects at this time.

> Modern FastAPI Project & Module Generator

FCube CLI is a powerful code generation tool that creates production-ready FastAPI projects and modules following clean architecture principles, dependency injection patterns, and role-based access control.

[![Python](https://img.shields.io/badge/Python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![FastAPI](https://img.shields.io/badge/Framework-FastAPI-009688.svg)](https://fastapi.tiangolo.com/)

---

## What is FCube?

**FCube** is a CLI tool that generates production-ready FastAPI projects with:

- **Complete Project Scaffolding** - Generate full FastAPI projects with core infrastructure
- **Modular User System** - Add user module with configurable authentication (email, phone, or both)
- **Plugin Architecture** - Pre-built feature modules with automatic validation
- **Modern Module Structure** - Organized directories for models, schemas, crud, services, routes
- **Docker Support** - docker-compose with PostgreSQL, Redis, Celery, and Flower
- **Alembic Migrations** - Pre-configured async migrations
- **Dependency Injection** - `@lru_cache` singleton services with factory functions
- **Role-Based Routes** - Separate public and admin route directories
- **Permission System** - RBAC with configurable permissions
- **Transaction Management** - "No Commit in CRUD" pattern
- **Rich CLI** - Beautiful terminal output with progress indicators

```bash
# Create a new project
fcube startproject MyApp

# Add user module with email authentication
fcube adduser --auth-type email

# Add referral plugin
fcube addplugin referral

# Create a custom module
fcube startmodule product

# Start the server
docker compose up -d
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

    Clean DI pattern with `@lru_cache()` singleton services for testability.

-   :material-database:{ .lg .middle } __Database Patterns__

    ---

    SQLAlchemy 2.0 ORM, async sessions, Alembic migrations, and "No Commit in CRUD" pattern.

-   :material-shield-check:{ .lg .middle } __Authentication__

    ---

    Configurable auth with email/password, phone OTP, or both.

-   :material-puzzle:{ .lg .middle } __Plugin System__

    ---

    Add pre-built features like referral systems or deployment configs.

-   :material-file-code:{ .lg .middle } __Code Generation__

    ---

    Templates for models, schemas, CRUD, services, and routes.

-   :material-docker:{ .lg .middle } __Docker Support__

    ---

    docker-compose with PostgreSQL, Redis, Celery, and Flower.

-   :material-security:{ .lg .middle } __RBAC Permissions__

    ---

    Role-based access control with scoped permissions.

</div>

---

## Quick Start

```bash
# Install FCube
pip install git+https://github.com/amal-babu-git/fcube.git

# Create a new project
fcube startproject MyApp

# Navigate to project
cd MyApp

# Add user module with email authentication
fcube adduser --auth-type email

# Add referral plugin
fcube addplugin referral

# Create a custom module
fcube startmodule product

# Start the server
docker compose up -d
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
