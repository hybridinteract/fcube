# Project Structure

This document outlines the standard project structure, engineering philosophy, and required conventions used across all our backend projects. It serves as the primary system instruction manual for both human developers and AI coding assistants to ensure structural consistency and code quality.

## 1. Architectural Philosophy

We use a **Modular Monolith** architecture based on **Domain-Driven Design (DDD)** principles. Instead of organizing files by technical concern (e.g., grouping all application models in one folder and all routes in another), we group by **Domain/Feature** (e.g., User, Module, Lead, Product).

### Core Principles
- **Separation of Concerns**: HTTP routing, business logic, and database access are strictly decoupled into independent layers.
- **Dependency Injection**: Utilize dependency injection frameworks or patterns (e.g., FastAPI's `Depends`) to pass database sessions, current context, user states, and configurations into the appropriate layers.
- **Asynchronous First**: All I/O bound operations (database calls, external HTTP requests, file access) must use `async/await` paradigms to maintain high throughput.
- **Strict Typing**: Use strong type hints along with strict validation models (e.g., Pydantic) to ensure predictable data schemas in and out.

---

## 2. Global Directory Structure

A typical project follows this structured top-level design:

```text
project_root/
├── app/
│   ├── apis/            # Aggregates domain routers into unified, versioned APIs (e.g., /v1)
│   ├── core/            # Application-wide singletons, configurations, and generic base classes
│   └── <feature_name>/  # Domain-specific modules containing encapsulated feature logic
├── deploy/              # Deployment scripts, docker-compose files, configs
├── migrations/          # Database migrations 
├── pyproject.toml       # Dependency management and project metadata
└── README.md
```

### The `app/core/` Directory
Contains foundational logic that applies to the entire application:
- **`settings.py`**: Global configuration and environment variable loading.
- **`database.py`**: Database engine and session lifecycles.
- **`crud.py`**: Generic base classes for database access (e.g., a generic `CRUDBase` class).
- **`exceptions.py` / `middleware.py`**: Global error handling, logging, and application-wide interceptors.

---

## 3. Feature Module Details

Every domain feature (e.g., `app/user/`) encapsulates its own vertical slice of the application. A standard feature folder contains the following structure:

```text
app/<feature_name>/
├── __init__.py
├── models/             # ORM entity classes defining database tables
├── schemas/            # Data validation/serialization models (Inputs/Outputs)
├── crud/               # Repository pattern classes exclusively for DB interactions
├── services/           # Core business logic layer orchestrating processes
├── routes/             # API endpoint definitions and HTTP request handling
├── dependencies.py     # Feature-specific dependency injection providers
├── enums.py            # Feature-level constants and enumerations
├── exceptions.py       # Domain-specific error classes
├── tasks.py            # Async background tasks (if applicable)
└── tests/              # Isolated unit and integration tests for this feature
```

---

## 4. Layer Responsibilities & Strict Rules

To maintain high maintainability, AI tools and developers **MUST** adhere to the following layer rules:

### A. Route Layer (`routes/`)
- **Purpose**: Manage incoming HTTP requests, parse inputs, invoke services, and format HTTP responses.
- **Rules**:
  - **NO BUSINESS LOGIC**: Do not write loops, conditionals based on state, or rule validations here.
  - **NO DATABASE QUERIES**: Do not directly query the ORM from a route.
  - Must rely completely on Dependency Injection to receive Services and Database context.
  - Catch domain exceptions (raised by Services) and translate them into appropriate HTTP status codes before returning.

### B. Service Layer (`services/`)
- **Purpose**: Execute core business rules, handle complex logic operations, and coordinate interactions between external systems, caching storage, or other domain services.
- **Rules**:
  - **Owns the Database Transaction Boundaries**: Services are strictly responsible for calling `session.commit()` or `session.rollback()`. 
  - Completely agnostic to the transport layer (e.g., Services should not know what an HTTP request/response object is).
  - Interacts with the data layer *exclusively* through the module's `crud/` layer instances.

### C. Data Access Layer (`crud/`)
- **Purpose**: Encapsulate SQL queries and atomic database operations behind clean, declarative Python interfaces.
- **Rules**:
  - Inherit generic behaviors from `app/core/crud.py` whenever possible.
  - **NEVER CALL `session.commit()` WITHIN CRUD**: The CRUD layer should only query data, add objects to the session (`session.add()`), or flush changes to obtain newly generated primary keys (`session.flush()`).
  - Keep methods purely data-centric, predictable, and devoid of business conditions.

### D. Schemas Layer (`schemas/`)
- **Purpose**: Define structured request and response validations.
- **Rules**:
  - Split schemas specifically by intent: Create, Update, Response, filters, etc. This prevents users from manually passing immutable fields to update endpoints.
  - Enforce strict input validation (string lengths, boundary values, Regex) at this level.

---

## 5. Workflow execution for AI Assistants & Developers

When implementing a new feature or endpoint, strictly follow this execution order:

1. **Define the Data Shape**: Start with `schemas/`. Define the Pydantic models for your incoming request, your updates, and your outward response.
2. **Setup the Database interactions**: Update the respective ORM methods in the `crud/` folder to build your queries. Remember to return ORM objects.
3. **Draft the Logic**: Implement the core business action in `services/`. Import your `crud` functions, perform verifications, flush/commit using the DB session, and return formatted data.
4. **Expose the Endpoint**: Navigate to `routes/`. Define the HTTP method (`GET`, `POST`, `PUT`, etc.). Inject the db session and the Service via the dependency system. Execute the service, catch any exceptions, and return the data utilizing your `schemas/` models for response typing.
5. **Add Tests**: Write functional module tests in `tests/` to guarantee coverage of the new behavior.

### Handling Errors globally

- **NEVER** return raw `HTTPException(status=500)` from deep inside Services or CRUD.
- Expected violations (e.g. data missing, insufficient permissions, limits exceeded) should be raised via custom Domain Exceptions defined within `exceptions.py`.
- Let the application's global exception handler or route try-catch block securely translate these to HTTP formatting to maintain a decoupled architecture.

---

## 6. AI Assistant System Prompt

Copy and paste the text block below into your IDE's AI rules (e.g., `.cursorrules`, GitHub Copilot Custom Instructions, or ChatGPT Custom Instructions) so the AI contextually understands our architecture and generates code that automatically adheres to our conventions.

```text
You are an expert Python backend developer working on a Modular Monolith architecture based on Domain-Driven Design (DDD). The stack primarily utilizes FastAPI, SQLAlchemy 2.0, and Pydantic. 

Whenever you generate code or suggest architecture, you MUST strictly adhere to the following rules:

### Directory Structure & Encapsulation
Features are grouped by domain vertically (e.g., `app/user/`), and typically contain:
- `models/`: SQLAlchemy ORM entity definitions.
- `schemas/`: Pydantic input/output schemas (split by intent: Create, Update, Response).
- `crud/`: SQL queries and atomic DB operations.
- `services/`: Core business logic orchestration.
- `routes/`: HTTP handlers and endpoints.

### Layer Responsibilities (STRICT RULES)
1. **Routes Layer (`routes/`)**:
   - Parses inputs, delegates to Services, maps Service exceptions, and returns HTTP responses.
   - STRICT RULE: NO business logic whatsoever (no state-based loops/conditionals).
   - STRICT RULE: NO direct ORM/database queries.
   - Must completely rely on Dependency Injection for context.
2. **Service Layer (`services/`)**:
   - Executes core business orchestration.
   - STRICT RULE: Owns DB transactions. You MUST explicitly commit (`session.commit()`) or rollback here.
   - STRICT RULE: Completely HTTP-agnostic (no `Request`/`Response` objects).
3. **CRUD Layer (`crud/`)**:
   - Clean Python interfaces for DB interactions ONLY.
   - STRICT RULE: NEVER call `session.commit()`. You may only query, `session.add()`, and `session.flush()`.
4. **Error Handling**:
   - Deep layers (Service/CRUD) MUST exclusively raise custom Python Exceptions representing domain errors.
   - STRICT RULE: NEVER throw raw `HTTPException` from Services or CRUD layers.

### Workflow Execution Order
When asked to build an endpoint or feature, execute and reason in this specific order:
1. Define the data boundaries in `schemas/`.
2. Construct pure DB interactions in `crud/` (returning ORM objects).
3. Orchestrate logic and transaction commits in `services/`.
4. Expose the HTTP endpoint in `routes/` using DI.
```
