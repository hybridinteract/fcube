# Architecture & Development Guide

Copy the text block below to use as an AI prompt (e.g., in `.cursorrules` or Claude/ChatGPT instructions) or simply share it as a reference guide for developers.

```markdown
This guide outlines the architecture and development conventions for our Modular Monolith based on Domain-Driven Design (DDD). The stack primarily utilizes FastAPI, SQLAlchemy 2.0, and Pydantic. It serves as a structured reference for both internal developers and AI coding assistants.

All codebase contributions and architectural additions MUST strictly adhere to the following rules:

### Directory Structure & Encapsulation
Features are grouped by domain vertically (e.g., `app/user/`), and typically contain:
- `models/`: SQLAlchemy ORM entity definitions.
- `schemas/`: Pydantic input/output schemas (split by intent: Create, Update, Response).
- `crud/`: SQL queries and atomic DB operations.
- `services/`: Core business logic orchestration.
- `routes/`: HTTP handlers and endpoints.
- `dependencies.py`: Module-level dependency injection.

### Application Modules & Loose Coupling
- Modules MUST be independent verticals. Cross-module communication happens ONLY through **Shared Services**, NEVER by importing another module's CRUD operations directly.
- E.g., The `lead` module needing user data should inject `user_query_service` (a read-only cross-module service).
- Use `__init__.py` to explicitly export public interfaces (Routes, Models, Public Services) so internal files stay hidden.

### Dependency Injection & Dependencies File (`dependencies.py`)
- Centralize all definitions in the module's `dependencies.py`.
- **Singletons**: Instantiate Services and CRUD classes as global singletons inside `dependencies.py` (e.g., `_my_service = MyService(my_crud=my_crud_instance)`).
- **FastAPI DI**: Expose these singletons via simple getter functions (`def get_my_service() -> MyService: return _my_service`) and inject into routes using FastAPI's `Depends()`.

### Layer Responsibilities (STRICT RULES)
1. **Routes Layer (`routes/`)**:
   - Parses inputs, delegates to Services, maps Service exceptions, and returns HTTP responses.
   - STRICT RULE: NO business logic whatsoever (no state-based loops/conditionals).
   - STRICT RULE: NO direct ORM/database queries.
   - Must completely rely on Dependency Injection for context.
2. **Service Layer (`services/`)**:
   - Executes core business orchestration.
   - **Design**: Must be created as Classes. Inject all required repositories (CRUD) or cross-module services through the `__init__` constructor.
   - **Execution**: Methods take execution context (e.g., `session: AsyncSession`, user IDs) as arguments, keeping the instance stateless.
   - STRICT RULE: Owns DB transactions. You MUST explicitly commit (`session.commit()`) or rollback here.
   - STRICT RULE: Completely HTTP-agnostic (no `Request`/`Response` objects).
3. **CRUD Layer (`crud/`)**:
   - Clean Python interfaces for DB interactions ONLY.
   - STRICT RULE: NEVER call `session.commit()`. You may only query, `session.add()`, and `session.flush()`.
4. **Error Handling**:
   - Deep layers (Service/CRUD) MUST exclusively raise custom Python Exceptions representing domain errors.
   - STRICT RULE: NEVER throw raw `HTTPException` from Services or CRUD layers.

### Workflow Execution Order
When building an endpoint or feature, execute and reason in this specific order:
1. Define the data boundaries in `schemas/`.
2. Construct pure DB interactions in `crud/` (returning ORM objects).
3. Orchestrate logic and transaction commits in `services/`.
4. Register the new Service / dependencies in `dependencies.py`.
5. Expose the HTTP endpoint in `routes/` using DI.
```
