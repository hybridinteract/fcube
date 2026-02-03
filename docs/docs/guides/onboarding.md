# Developer Onboarding

Welcome to the team! Here's everything you need to get productive.

---

## Week 1 Goals

By the end of your first week, you should:

- [ ] Have your development environment set up
- [ ] Be able to run the application locally
- [ ] Understand the project structure
- [ ] Make your first commit
- [ ] Know who to ask for help

---

## Environment Setup

### 1. Required Tools

Install these tools:

| Tool | Version | Purpose |
|------|---------|---------|
| **Python** | 3.11+ | Backend runtime |
| **Node.js** | 20+ | Frontend runtime |
| **Docker** | 24+ | Containerization |
| **PostgreSQL** | 15+ | Database |
| **Redis** | 7+ | Cache/Queue |
| **Git** | 2.40+ | Version control |

### 2. Clone Repositories

```bash
# Backend
git clone git@github.com:hybridinteract/project-backend.git
cd project-backend

# Frontend (in separate terminal)
git clone git@github.com:hybridinteract/project-frontend.git
cd project-frontend
```

### 3. Backend Setup

```bash
cd project-backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Linux/Mac
# .\venv\Scripts\activate  # Windows

# Install dependencies
pip install -r requirements.txt
pip install -r requirements-dev.txt

# Copy environment file
cp .env.example .env
# Edit .env with your local settings

# Run database migrations
alembic upgrade head

# Start the server
uvicorn app.main:app --reload
```

### 4. Frontend Setup

```bash
cd project-frontend

# Install dependencies
npm install

# Copy environment file
cp .env.example .env.local
# Edit as needed

# Start dev server
npm run dev
```

### 5. Verify Setup

- Backend: [http://localhost:8000/docs](http://localhost:8000/docs)
- Frontend: [http://localhost:3000](http://localhost:3000)

---

## IDE Setup

### VS Code (Recommended)

Install these extensions:

| Extension | Purpose |
|-----------|---------|
| Python | Python support |
| Pylance | Type checking |
| Black Formatter | Code formatting |
| ESLint | JS/TS linting |
| Prettier | JS/TS formatting |
| GitLens | Git integration |

**Workspace Settings** (`.vscode/settings.json`):

```json
{
  "editor.formatOnSave": true,
  "python.defaultInterpreterPath": "./venv/bin/python",
  "[python]": {
    "editor.defaultFormatter": "ms-python.black-formatter"
  },
  "[typescript]": {
    "editor.defaultFormatter": "esbenp.prettier-vscode"
  }
}
```

### PyCharm

1. Open project directory
2. Configure Python interpreter (select venv)
3. Enable Black formatter (Settings → Tools → Black)
4. Configure pytest as test runner

---

## Project Overview

### Architecture

```
┌─────────────────┐     ┌─────────────────┐
│    Frontend     │────▶│     Backend     │
│   (Next.js)     │     │   (FastAPI)     │
└─────────────────┘     └────────┬────────┘
                                 │
                    ┌────────────┼────────────┐
                    │            │            │
              ┌─────▼────┐ ┌─────▼────┐ ┌─────▼────┐
              │PostgreSQL│ │  Redis   │ │  Celery  │
              └──────────┘ └──────────┘ └──────────┘
```

### Key Directories

| Directory | Contains |
|-----------|----------|
| `app/models/` | Database models |
| `app/schemas/` | API schemas (Pydantic) |
| `app/services/` | Business logic |
| `app/routes/` | API endpoints |
| `app/core/` | Configuration, database, auth |

---

## Making Your First Commit

### 1. Pick a Starter Task

Your manager will assign you a small task tagged as `good-first-issue`.

### 2. Create a Branch

```bash
git checkout -b feature/your-task-name
```

### 3. Make Changes

Write code following our [Best Practices](../principles/best-practices.md).

### 4. Test Locally

```bash
# Run tests
pytest

# Check linting
ruff check .
black --check .
```

### 5. Commit and Push

```bash
git add .
git commit -m "feat(module): description of change"
git push origin feature/your-task-name
```

### 6. Open a Pull Request

Go to GitHub and open a PR. See [Git Workflow](git-workflow.md) for details.

---

## Getting Help

| Question Type | Where to Ask |
|---------------|--------------|
| **Code question** | Ask your **buddy** (assigned mentor) |
| **Architecture question** | #engineering Slack channel |
| **Stuck on a bug** | Create a minimal repro, ask in #help |
| **Infrastructure issue** | #devops Slack channel |

### Pair Programming

Don't struggle alone! Schedule a pairing session:

- For learning: Pair with your buddy
- For tough bugs: Pair with senior engineer
- For design decisions: Pair with tech lead

---

## Key Resources

| Resource | Location |
|----------|----------|
| API Documentation | [localhost:8000/docs](http://localhost:8000/docs) |
| Design System | [Figma Link] |
| Architecture Docs | This site |
| Internal Wiki | [Notion Link] |
| Sprint Board | [Jira/Linear Link] |

---

## Checklist

### Day 1

- [ ] Accounts created (GitHub, Slack, Jira)
- [ ] Repositories cloned
- [ ] Meet your buddy

### Day 2-3

- [ ] Environment fully set up
- [ ] Can run backend and frontend
- [ ] Read through project README

### Day 4-5

- [ ] First task assigned
- [ ] First PR opened
- [ ] First PR merged! 🎉

---

## FAQ

**Q: I can't connect to the database**

Check that PostgreSQL is running and your `DATABASE_URL` in `.env` is correct.

**Q: Tests are failing but I didn't change anything**

Pull latest `main` and re-run migrations:
```bash
git checkout main
git pull
alembic upgrade head
```

**Q: How do I get my PR reviewed faster?**

Keep PRs small (< 400 lines), write a clear description, and tag reviewers.
