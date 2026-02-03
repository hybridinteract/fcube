# Getting Started

Install FCube and create your first project.

---

## Installation

### Prerequisites

- **Python 3.11+** — Check with `python --version`
- **pip** — Usually included with Python

### Install from PyPI

```bash
pip install fcube
```

### Verify Installation

```bash
fcube --version
# FCube CLI v1.0.0
```

---

## Create Your First Project

### 1. Generate Project

```bash
fcube startproject myapp
```

This creates:

```
myapp/
├── app/
│   ├── __init__.py
│   ├── main.py              # FastAPI application
│   ├── apis/
│   │   └── v1.py            # API router (v1)
│   ├── core/
│   │   ├── config.py        # Settings
│   │   ├── database.py      # Database connection
│   │   ├── dependencies.py  # DI container
│   │   └── security.py      # Auth utilities
│   ├── models/              # SQLAlchemy models
│   ├── schemas/             # Pydantic schemas
│   ├── services/            # Business logic
│   └── crud/                # Database operations
├── alembic/                 # Database migrations
├── tests/                   # Test suite
├── requirements.txt
├── .env.example
└── README.md
```

### 2. Set Up Environment

```bash
cd myapp

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Linux/Mac
# or: .\venv\Scripts\activate  # Windows

# Install dependencies
pip install -r requirements.txt
```

### 3. Configure Database

```bash
# Copy example env
cp .env.example .env

# Edit .env with your database URL
# DATABASE_URL=postgresql://user:pass@localhost:5432/myapp
```

### 4. Run Migrations

```bash
alembic upgrade head
```

### 5. Start the Server

```bash
uvicorn app.main:app --reload
```

Open [http://localhost:8000/docs](http://localhost:8000/docs) — you'll see the Swagger UI!

---

## Add a Module

Modules are feature-based groupings of your code.

```bash
fcube addmodule products
```

This generates:

```
app/
├── models/products.py       # SQLAlchemy model
├── schemas/products.py      # Pydantic schemas
├── crud/products.py         # CRUD operations
├── services/products.py     # Business logic
└── routes/products.py       # API endpoints
```

**Routes are automatically registered** in `app/apis/v1.py`.

---

## Add Authentication

```bash
fcube adduser --jwt
```

This adds:

- User model with password hashing
- JWT token authentication
- Login/register endpoints
- Role-based permissions
- Refresh token support

### Using Auth

```python
from app.core.dependencies import get_current_user
from app.models.user import User

@router.get("/me")
async def get_profile(user: User = Depends(get_current_user)):
    return user
```

---

## Add a Plugin

Plugins add pre-built features to your project.

```bash
# See available plugins
fcube plugins

# Add a plugin
fcube addplugin referral
```

Learn more in the [Plugin System](plugins.md) guide.

---

## Project Configuration

### Environment Variables

```bash
# .env
DATABASE_URL=postgresql://user:pass@localhost:5432/myapp
REDIS_URL=redis://localhost:6379/0
SECRET_KEY=your-secret-key
JWT_SECRET_KEY=your-jwt-secret
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
```

### Settings Management

```python
# app/core/config.py
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    database_url: str
    redis_url: str = "redis://localhost:6379/0"
    secret_key: str
    jwt_secret_key: str
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    
    class Config:
        env_file = ".env"


settings = Settings()
```

---

## Next Steps

1. **Learn the commands** — See [Commands Reference](commands.md)
2. **Understand the architecture** — Read [Generated Architecture](architecture.md)
3. **Explore plugins** — Check [Plugin System](plugins.md)
4. **Deploy your app** — Use the `deploy-vps` plugin

---

## Common Issues

### Can't connect to database

```bash
# Check PostgreSQL is running
pg_isready

# Verify DATABASE_URL format
postgresql://user:password@host:port/database
```

### Module not found after generation

```bash
# Ensure you're in virtual environment
source venv/bin/activate

# Reinstall in development mode
pip install -e .
```

### Migrations fail

```bash
# Check alembic.ini has correct sqlalchemy.url
# Or set env variable and run:
alembic upgrade head
```
