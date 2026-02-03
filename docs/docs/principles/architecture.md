# Architecture & Tech Stack

This guide documents our system design philosophy, technology choices, and deployment strategies. It's a reference for engineers to understand **why** we build the way we do, based on trade-offs between speed, complexity, and scalability.

---

## Architectural Approach: Modular Monolith

We build **modular monoliths**—single deployable applications with well-defined internal boundaries. Each module (e.g., `user`, `product`, `booking`) has its own models, services, and routes, deployed together as a cohesive unit.

This architecture provides the simplicity and development speed of a monolith while maintaining the structural clarity and maintainability benefits of modular design. Modules are loosely coupled and can be independently developed, tested, and potentially extracted into separate services if future scalability needs require it.

We use the **FCube CLI** to automatically scaffold projects and modules with this standardized architecture, ensuring consistency across all applications.

[:octicons-arrow-right-24: View FCube Guide](../fcube/index.md)

---

## Backend Stack

Our backend is built on **Python** and **FastAPI**, designed for rapid development and high performance.

### Core Technologies

| Technology | Purpose |
|------------|---------|
| **FastAPI** | Async REST API framework. API-first design with automatic OpenAPI docs. |
| **SQLAlchemy 2.0** | ORM with async support for database operations. |
| **Pydantic** | Data validation and serialization (schemas). |
| **Alembic** | Database migrations for schema changes. |
| **Celery** | Distributed task queue for background jobs (emails, reports, etc.). |
| **Redis** | Caching, session storage, and Celery message broker. |
| **PostgreSQL** | Primary relational database. |

### Why FastAPI?

FastAPI is a modern Python framework with an **API-first approach**. Key advantages:

1.  **Performance**: Built on Starlette and Pydantic, it's one of the fastest Python frameworks available.
2.  **Async Native**: First-class support for `async`/`await`, critical for I/O-bound workloads.
3.  **Automatic Docs**: OpenAPI (Swagger) and ReDoc are generated automatically.
4.  **Type Safety**: Leverages Python type hints for validation and editor support.

### Python Scalability Considerations

Python is a versatile language that scales effectively for most real-world applications. While it has known limitations with CPU-bound workloads due to the Global Interpreter Lock (GIL), these can be mitigated with appropriate architectural patterns:

#### Scaling Strategies by Workload Type

| Workload Type | Approach |
|---------------|----------|
| **I/O-Bound Tasks** | FastAPI's async support enables high concurrency for database and network operations (using async drivers and proper connection pooling) |
| **CPU-Bound Tasks** | Offload to **Celery workers** running as separate processes to bypass the GIL |
| **Heavily CPU-Bound Workloads** | Isolate into dedicated worker services (e.g., Go, Rust) called via REST or gRPC. This is reserved for specific use cases like ML inference or video processing |

In practice, **scalability is almost always a database or infrastructure problem, not a language problem**. Proper database indexing, query optimization, and infrastructure scaling (vertical/horizontal) address most performance needs.

---

## Layered Architecture

We follow a strict **Layered Architecture** pattern. Each layer has a single responsibility, and dependencies only point downwards.

```
┌─────────────────────────────────────┐
│          Routes (HTTP Layer)        │  ← Request/Response handling, Auth
└───────────────┬─────────────────────┘
                │
┌───────────────▼─────────────────────┐
│        Services (Business Logic)    │  ← Orchestration, transactions
└───────────────┬─────────────────────┘
                │
┌───────────────▼─────────────────────┐
│         CRUD (Data Access)          │  ← Pure DB operations, NO commit
└───────────────┬─────────────────────┘
                │
┌───────────────▼─────────────────────┐
│        Models (Database Schema)     │  ← SQLAlchemy ORM definitions
└─────────────────────────────────────┘
```

### Key Rules

1.  **Routes** handle HTTP concerns (request parsing, response serialization, authentication). They call Services.
2.  **Services** contain business logic. They orchestrate multiple CRUD operations and **own the transaction** (call `session.commit()`).
3.  **CRUD** performs pure database operations. **CRUD methods never call `commit()`**. They use `flush()` and `refresh()` only.
4.  **Models** define the database schema using SQLAlchemy ORM.

This pattern ensures testability, separation of concerns, and clear transaction boundaries.

---

## Frontend Stack

Our frontend is built with **React** and **Next.js**, using **TypeScript** for type safety.

| Technology | Purpose |
|------------|---------|
| **React 18+** | Component-based UI library. |
| **Next.js 14+** | React framework with SSR, routing, and API routes. |
| **TypeScript** | Static typing for JavaScript. |
| **Tailwind CSS** | Utility-first CSS framework. |
| **DaisyUI / shadcn/ui** | Pre-built UI component libraries. |
| **Axios** | HTTP client for API communication. |

---

## Deployment Strategies

We have three deployment approaches for backend, and a dedicated frontend deployment strategy.

### Frontend Deployment (Next.js)

We primarily deploy Next.js applications on **Vercel** due to its native support for Next.js features:

*   **Server-Side Rendering (SSR)**: For SEO-critical pages that need fast initial loads
*   **Static Site Generation (SSG)**: For pre-rendering content at build time
*   **Edge Functions**: For serverless logic at the CDN edge
*   **Automatic Scaling**: Handles traffic spikes automatically
*   **Git Integration**: Seamless deployment from GitHub/GitLab branches

Vercel provides optimal performance for Next.js applications, with built-in support for features like incremental static regeneration and edge caching.

### Backend Deployment Strategies

#### 1. Docker Compose (Testing & Small Production)

For staging environments and small-scale production.

*   **Components**: Nginx, FastAPI, Celery (Worker + Beat), Flower, Redis, Certbot (all in Docker Compose).
*   **Database**: Managed PostgreSQL (external) or self-hosted PostgreSQL container.
*   **Infra**: Single VPS (e.g., DigitalOcean Droplet, EC2 instance).
*   **Best For**: Staging, internal tools, low-traffic applications.

=== "Infrastructure View"

    ```mermaid
    graph TB
        subgraph Internet
            Users[Users/Browser]
            Vercel[Vercel<br/>Next.js Frontend]
        end

        subgraph "Single VM/VPS"
            subgraph "Docker Compose"
                Nginx[Nginx<br/>Reverse Proxy + SSL]
                Certbot[Certbot<br/>SSL Certificates]
                API[FastAPI App<br/>Gunicorn + Uvicorn]
                Redis[Redis<br/>Cache + Broker]
                CeleryWorker[Celery Worker<br/>Background Tasks]
                CeleryBeat[Celery Beat<br/>Scheduler]
                Flower[Flower<br/>Monitoring]
            end
        end

        ManagedDB[(Managed PostgreSQL<br/>External Service)]

        Users -->|HTTPS| Nginx
        Vercel -->|API Calls| Nginx
        Nginx --> API
        Nginx --> Flower
        API --> Redis
        API --> ManagedDB
        CeleryWorker --> Redis
        CeleryWorker --> ManagedDB
        CeleryBeat --> Redis
    ```

=== "Data Flow View"

    ```mermaid
    graph TD
        User((User/Browser)) -->|Initial Page Request| Vercel[Vercel/Next.js]
        Vercel -->|SSR Data Fetch| Nginx[Nginx :443]
        Nginx -->|Proxy| API[FastAPI App :8000]
        API -->|Response| Nginx
        Nginx -->|Response| Vercel
        Vercel -->|HTML Response| User

        User -->|Client-Side API Calls| Nginx
        Nginx -->|Proxy| API
        API -->|JSON Response| Nginx
        Nginx -->|JSON Response| User

        API -->|Query| DB[(Managed PostgreSQL)]
        API -->|Cache Read/Write| Redis[(Redis :6379)]
        API -->|Queue Task| Redis

        CeleryWorker[Celery Worker] -->|Poll Jobs| Redis
        CeleryWorker -->|Execute| DB
        CeleryBeat[Celery Beat] -->|Schedule| Redis

        Flower[Flower :5555] -->|Monitor| Redis
        User -->|Admin Access| Nginx
        Nginx -->|Proxy /flower| Flower
    ```

#### 2. Stateless App + Managed Services (Primary Production)

Our most common production deployment. The application is stateless and easy to scale horizontally.

*   **Application**: Multiple stateless FastAPI VMs behind a load balancer.
*   **Database**: Managed PostgreSQL (e.g., DigitalOcean Managed Database, AWS RDS).
*   **Cache**: Managed Redis (e.g., DigitalOcean Managed Redis, AWS ElastiCache).
*   **Scaling**: Add more VMs behind the load balancer as traffic grows.

!!! tip
    This approach handles the vast majority of applications. Most apps will scale effectively with a managed database and a few VMs behind a load balancer.

=== "Infrastructure View"

    ```mermaid
    graph TB
        subgraph Internet
            Users[Users/Browser]
            Vercel[Vercel<br/>Next.js Frontend]
        end

        LB[Load Balancer<br/>HTTPS/SSL Termination]

        subgraph "Application VMs"
            VM1[VM 1<br/>FastAPI + Celery]
            VM2[VM 2<br/>FastAPI + Celery]
            VM3[VM 3<br/>FastAPI + Celery]
        end

        subgraph "Managed Services"
            ManagedDB[(Managed PostgreSQL)]
            ManagedRedis[(Managed Redis)]
        end

        Users -->|HTTPS| LB
        Vercel -->|API Calls| LB
        LB --> VM1
        LB --> VM2
        LB --> VM3

        VM1 --> ManagedDB
        VM2 --> ManagedDB
        VM3 --> ManagedDB

        VM1 --> ManagedRedis
        VM2 --> ManagedRedis
        VM3 --> ManagedRedis
    ```

=== "Data Flow View"

    ```mermaid
    graph TD
        User((User/Browser)) -->|Initial Page Request| Vercel[Vercel/Next.js]
        Vercel -->|SSR Data Fetch| LB[Load Balancer]
        LB -->|Proxy| VM1[FastAPI VM 1]
        LB -->|Proxy| VM2[FastAPI VM 2]
        VM1 -->|Response| LB
        VM2 -->|Response| LB
        LB -->|Response| Vercel
        Vercel -->|HTML Response| User

        User -->|Client-Side API Calls| LB
        LB -->|Proxy| VM1
        LB -->|Proxy| VM2
        VM1 -->|JSON Response| LB
        VM2 -->|JSON Response| LB
        LB -->|JSON Response| User

        VM1 -->|Query| ManagedDB[(Managed PostgreSQL)]
        VM2 -->|Query| ManagedDB

        VM1 -->|Cache + Queue| ManagedRedis[(Managed Redis)]
        VM2 -->|Cache + Queue| ManagedRedis

        subgraph "VM 1 Services"
            API1[FastAPI]
            Celery1[Celery Worker]
        end

        subgraph "VM 2 Services"
            API2[FastAPI]
            Celery2[Celery Worker]
        end

        Celery1 -->|Poll Jobs| ManagedRedis
        Celery2 -->|Poll Jobs| ManagedRedis
        Celery1 -->|Execute| ManagedDB
        Celery2 -->|Execute| ManagedDB
    ```

#### 3. Container Orchestration (High Scale)

For applications requiring auto-scaling and high availability.

*   **Platform**: AWS ECS (Fargate), Google Cloud Run, or Kubernetes.
*   **Application**: Stateless FastAPI container images with auto-scaling.
*   **Background Jobs**: Separate Celery worker containers with independent scaling.
*   **Data**: Managed database and Redis instances.
*   **Scaling**: Automatic scaling based on CPU/memory or request count.

This is reserved for applications with significant traffic or strict availability requirements.

=== "Infrastructure View"

    ```mermaid
    graph TB
        subgraph Internet
            Users[Users/Browser]
            Vercel[Vercel<br/>Next.js Frontend]
        end

        subgraph "Container Orchestration Platform"
            subgraph "API Service<br/>(Auto-scaling)"
                Container1[FastAPI<br/>Container 1]
                Container2[FastAPI<br/>Container 2]
                Container3[FastAPI<br/>Container 3]
                ContainerN[FastAPI<br/>Container N]
            end

            subgraph "Worker Service<br/>(Auto-scaling)"
                Worker1[Celery Worker<br/>Container 1]
                Worker2[Celery Worker<br/>Container 2]
                WorkerN[Celery Worker<br/>Container N]
            end

            subgraph "Scheduler Service"
                Beat[Celery Beat<br/>Container]
            end
        end

        subgraph "Managed Services"
            ManagedDB[(Managed PostgreSQL<br/>Read Replicas)]
            ManagedRedis[(Managed Redis<br/>Cluster Mode)]
        end

        LB[Load Balancer/Ingress<br/>ALB/NLB/Ingress Controller]

        Users -->|HTTPS| LB
        Vercel -->|API Calls| LB

        LB --> Container1
        LB --> Container2
        LB --> Container3

        Container1 --> ManagedDB
        Container2 --> ManagedDB
        Container3 --> ManagedDB

        Container1 --> ManagedRedis
        Container2 --> ManagedRedis
        Container3 --> ManagedRedis

        Worker1 --> ManagedRedis
        Worker2 --> ManagedRedis
        Worker1 --> ManagedDB
        Worker2 --> ManagedDB

        Beat --> ManagedRedis
    ```

=== "Data Flow View"

    ```mermaid
    graph TD
        User((User/Browser)) -->|Initial Page Request| Vercel[Vercel/Next.js]
        Vercel -->|SSR Data Fetch| Cluster[Container Cluster<br/>Load Balancer]
        Cluster -->|Route| Container1[FastAPI Container 1]
        Cluster -->|Route| Container2[FastAPI Container 2]
        Cluster -->|Route| Container3[FastAPI Container 3]
        Container1 -->|Response| Cluster
        Container2 -->|Response| Cluster
        Container3 -->|Response| Cluster
        Cluster -->|Response| Vercel
        Vercel -->|HTML Response| User

        User -->|Client-Side API Calls| Cluster
        Cluster -->|JSON Response| User

        Container1 -->|Query| ManagedDB[(Managed PostgreSQL)]
        Container2 -->|Query| ManagedDB
        Container3 -->|Query| ManagedDB

        Container1 -->|Cache + Queue| ManagedRedis[(Managed Redis)]
        Container2 -->|Cache + Queue| ManagedRedis
        Container3 -->|Cache + Queue| ManagedRedis

        CeleryWorkers[Celery Worker Containers] -->|Poll Jobs| ManagedRedis
        CeleryWorkers -->|Execute Tasks| ManagedDB

        CeleryBeat[Celery Beat Container] -->|Schedule Jobs| ManagedRedis

        Container1 -.->|Queue Task| ManagedRedis
        Container2 -.->|Queue Task| ManagedRedis
        Container3 -.->|Queue Task| ManagedRedis
    ```

---

## Quick Reference

| Layer | Technology | Version |
|-------|------------|---------|
| **Language** | Python | 3.11+ |
| **Framework** | FastAPI | 0.115+ |
| **ORM** | SQLAlchemy | 2.0+ |
| **Validation** | Pydantic | 2.0+ |
| **Task Queue** | Celery | 5.4+ |
| **Database** | PostgreSQL | 15+ |
| **Cache** | Redis (server) | 7.0+ |
| **Frontend** | Next.js | 14+ |
| **UI Library** | React | 18+ |
| **Type System** | TypeScript | 5.0+ |
