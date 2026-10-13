# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Commands

```bash
# Dev server (with reload)
poetry run dev

# Background workers
poetry run worker        # Celery
poetry run nats_worker   # NATS/JetStream

# Tests
ENV=test poetry run pytest
ENV=test poetry run pytest tests/app/routers/test_workflow.py::test_create_workflow  # single test

# Database migrations
alembic upgrade head
```

## Architecture

Orcha is a visual workflow automation backend built with FastAPI + SQLAlchemy (async, PostgreSQL). It orchestrates event-driven workflows composed of typed nodes connected by edges.

**Layers:**
- `app/routers/` — FastAPI route handlers (thin: delegate to repositories/commands)
- `app/commands/` — Complex multi-step operations (create, update, delete, execute)
- `app/repositories/` — Query/CRUD logic wrapping SQLAlchemy sessions (repository pattern)
- `app/models/` — SQLAlchemy ORM models
- `app/schemas/` — Pydantic request/response models

**Async task processing:**
- Celery + Redis for background jobs (`run_worker.py`)
- NATS JetStream via FastStream for event streaming (`run_nats_worker.py`)

**Auth/RBAC:** Handled globally by `RBACMiddleware` — no per-route auth logic needed. Method-to-action mapping: GET→read, POST→create, PUT/PATCH→update, DELETE→delete. Skip paths configured in `main.py`. Current user available via `request.state.user`.

## Patterns

### Repositories
- Class named `<Model>Repository`, takes `Session` in constructor
- Methods: `get_<model>()`, `get_<models>()`, `create_<model>()`, `update_<model>()`, `delete_<model>()`
- Use `model.model_dump()` for Pydantic → dict; always `commit()` and `refresh()` after writes
- Inherit from `SoftDeleteRepository` for soft-delete support

### Routers
- List endpoints: `Page[T]` with `paginate(query)` from `fastapi_pagination.ext.sqlalchemy`
- Single-item endpoints: return schema directly (no wrapper)
- POST returns 201, DELETE returns 204
- No underscores in path segments — use hyphens
- Nested resources: parent resolved via `Depends(get_<parent>_by_id)`, never from request body
- Exception handling: `ValueError` → 404 if "not found", else 400; re-raise `HTTPException`; generic `Exception` → 500

### Commands
- Used for complex operations in `app/commands/`
- Encapsulate validation + business logic; return the modified entity

### Tests
- Fixtures in `tests/fixtures/<entity>_fixtures.py`, named `setup_<model>` or `setup_<context>_<model>`
- Use `faker` for realistic test data
- Each test runs in a rolled-back transaction (session-scoped isolation)
- Auth is mocked — `request.state.user` is set to a test user automatically

## Database migrations

- Migrations run only in the API's `start.sh`. During a deploy, old and new containers overlap (the API rolls; workers deploy separately), so every migration must work with the previous release's code.
- One release: additive changes (nullable column or one with a server default, table, index).
- Two releases: dropping or renaming a column or table, adding `NOT NULL`, or changing a type. Release 1 stops reading and writing it; a later release runs the migration.
- See [Database migrations](https://github.com/mylinden-tech/infra/blob/main/docs/linden-continuous-delivery.md#database-migrations) and mylinden-tech/infra#260.
