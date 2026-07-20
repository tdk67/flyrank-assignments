# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Repository overview

This repo holds a series of independent Flyrank backend assignments, each in its own top-level directory. Each assignment is self-contained (own dependencies, own `.gitignore`) and builds on the previous one — read the earlier assignment before modifying a later one that says it extends it.

- `BE-01-FastAPI/` — assignment BE-01. A minimal single-file FastAPI service (`main.py`) with `POST /user` and `GET /user/{user_id}`, backed by an in-memory dict. No database, no persistence across restarts.
- `BE-04-Containerize/` — assignment BE-04. Takes BE-01 and upgrades it to a layered, containerized service backed by PostgreSQL, with Liquibase-managed migrations, plus a new `Task` domain (assignment/status lifecycle). This is the actively developed project; BE-01 is left as-is as a historical reference.

There is no root-level build system, package manifest, or test runner — each assignment directory is independent. Always `cd` into the relevant assignment directory before running any command below.

No linter or formatter is configured in either project. BE-01 has no automated tests — verify changes by running the app and exercising endpoints with `curl`. BE-04 has a pytest suite (see below).

---

## BE-01-FastAPI

```bash
cd BE-01-FastAPI
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
uvicorn main:app --reload          # http://127.0.0.1:8000, docs at /docs
```

Everything (Pydantic models, in-memory store, routes, validation error handler) lives in the single `main.py`. Requests with unknown fields are rejected (`ConfigDict(extra="forbid")`) rather than silently ignored — that behavior is intentional and preserved in BE-04.

---

## BE-04-Containerize

### Running

Recommended: full stack via Docker Compose (from inside `BE-04-Containerize/`):

```bash
cp .env.example .env               # first time only; .env is gitignored
docker compose up --build
```

This starts three services in dependency order: `db` (Postgres 16, with a named volume for persistence) → `db-migrate` (runs Liquibase changesets, then exits) → `web` (FastAPI on port 8000, waits for migrations to complete). `docker compose down -v` fully resets the DB volume (needed if you change Postgres credentials in `.env`).

Local (no Docker) API run against the Dockerized DB:

```bash
docker compose up -d db
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
# in .env, set POSTGRES_HOST=localhost
uvicorn main:app --host 127.0.0.1 --port 8000 --reload
```

Quick health/smoke check: `curl -i http://localhost:8000/health` should return `{"status": "healthy", "database": "connected"}`.

### Architecture: layered, port/adapter style

Request flow: `api/routes/*` → `services/*` → `repositories/*` (via a `*_repository_port.py` ABC interface) → `models.py` (SQLAlchemy ORM) → Postgres.

- **`main.py`** — composition root; creates the FastAPI app and registers routers. No business logic here.
- **`api/routes/`** — HTTP-only concerns (parsing, status codes, response shaping). One router file per domain (`user_routes.py`, `task_routes.py`, `health_routes.py`).
- **`services/`** — all business rules live here. This is the layer to change when adding a rule, not the routes.
  - `UserService` — user CRUD.
  - `TaskService` — task creation/metadata update and the task **status state machine** (see below).
  - `UserTaskService` — cross-domain coordination (assignment, unassignment, and the delete-safety check that a user with active task assignments cannot be deleted). Exists specifically so `UserService` doesn't need to know about the task domain.
  - `service_factories.py` — builds a service instance wired to a request-scoped `Session` (used from route dependencies, not a global DI container).
- **`repositories/`** — SQLAlchemy-backed persistence adapters, one pair per domain: a `*_port.py` ABC defining the interface and a concrete implementation. Services depend only on the port interface — swapping storage backends (e.g. BE-01's in-memory dict → this Postgres repo) changes only the repository layer, not services or routes. Preserve this boundary when extending the code.
- **`dtos/`** — internal transport objects that decouple the domain/service layer from both the HTTP schemas and the ORM models.
- **`schemas.py`** — the Pydantic API contract (request/response validation). Like BE-01, uses `ConfigDict(extra="forbid")` to reject unknown request fields with a 422.
- **`models.py`** — SQLAlchemy ORM table definitions.
- **`config.py`** — `pydantic-settings` `Settings`, loads Postgres credentials from `.env` and assembles the DSN. Username/password are `quote_plus`-escaped before being placed in the connection URL since credentials are untrusted input that may contain reserved URI characters (`@`, `:`, `/`, etc.).
- **`database.py`** — SQLAlchemy engine and the `Session` dependency used by routes.

### Task lifecycle (state machine, enforced in `TaskService`)

Deliberately split into narrow single-purpose endpoints instead of one generic PATCH:

- `POST /task` — create with only `name` + `description`; all lifecycle fields default.
- `PATCH /task/{task_id}` — metadata only (`name`, `description`, `estimated_duration_days`, `start_date`, `end_date`).
- `PATCH /task/{task_id}/assignee` — assignment only.
- `PATCH /task/{task_id}/status` — status transition only.

Allowed transitions: `PLANNED → ASSIGNED → STARTED → DONE`, `STARTED → FAILED`, `FAILED → STARTED`. An invalid transition returns `409 Conflict` with a business-rule message — do not let routes or repositories bypass this check.

A task has a single current `assignee_user_id`. `POST /users/{user_id}/tasks/unassign` clears a user's assignments back to `PLANNED`; `DELETE /user/{user_id}` is rejected (`409`) while the user still has assigned tasks — this check lives in `UserTaskService`, not `UserService`.

### Migrations (Liquibase)

Schema changes go in a new numbered SQL file under `db/changelog/changesets/` (formatted-SQL style, see `001_create_users_table.sql` / `002_create_tasks_tables.sql`), then registered in `db/changelog/db.changelog-master.xml`. Migrations run automatically via the `db-migrate` compose service before `web` starts — there is no separate manual migration command to remember. `migrate.Dockerfile` exists only because the upstream `liquibase/liquibase` image lacks a bundled Postgres JDBC driver; it adds the driver jar explicitly.

### Testing

```bash
docker compose up -d db          # only the db needs to be running
pip install -r requirements-dev.txt
pytest
```

- `tests/unit/` — services tested against in-memory fakes of the repository ports (`tests/unit/fakes.py`), no DB.
- `tests/integration/` — builds a real `<POSTGRES_DB>_test` database by replaying the actual Liquibase changeset files (not `Base.metadata.create_all()` from `models.py`), seeds a fixed dataset (`tests/fixtures/sample_data.json`), and drives the app through FastAPI's `TestClient`. Each test rolls back its own transaction (see `tests/conftest.py`), so tests never see each other's writes.
- Replaying the real changesets is deliberate: it's what caught (and, in `tests/integration/test_task_api.py::test_get_task_includes_lifecycle_timestamps`, still guards) drift between `models.py` and the migration files — see the Gotchas note on changeset 003 below.

### Gotchas

- `models.py`'s `Task` model and the migrations that create the `tasks` table can drift silently if a new column is added to one but not the other — changeset `002_create_tasks_tables.sql` originally didn't create `assigned_at`/`started_at`/`finished_at`/`failed_at`, which `models.py` already declared; this surfaced as a `psycopg2.errors.UndefinedColumn` at insert time. Fixed via a new changeset (`003_add_task_lifecycle_timestamps.sql`) — never edit an already-applied changeset in place, since Liquibase checksum-validates them; always add a new one.
- Changing Postgres credentials in `.env` does not take effect against an existing volume — run `docker compose down -v` then bring `db` back up before re-migrating.
- If `web` can't find tables, check that `db-migrate` actually completed (`docker compose up --build db-migrate`) before assuming an app-level bug.
