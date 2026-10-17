# Python Skills Demo — Backend

FastAPI backend scaffolding demonstrating a clean layered architecture:

- **API layer** — thin routers with versioning (`/api/v1/`)
- **Service layer** — business logic
- **CRUD layer** — generic + model-specific database operations
- **ORM models** — SQLAlchemy 2.0 declarative
- **Pydantic schemas** — request/response validation (DTOs)
- **Security** — bcrypt password hashing, JWT auth
- **Alembic** — database migrations

## Quick Start

```bash
cd backend
uv venv .venv && source .venv/bin/activate
uv pip install -e ".[dev]"
uvicorn app.main:app --reload
```

API docs: http://localhost:8000/docs

## Running Tests

```bash
pytest
```
