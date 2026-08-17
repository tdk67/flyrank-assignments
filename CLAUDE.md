# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Proof Statement
"I bring nearly 30 years of software engineering
experience to build and reliably integrate modern AI features, specifically RAG
applications, into complex enterprise backend infrastructures. This proof is built for an
Engineering Manager at a large, international enterprise who needs a veteran developer
capable of bridging established backend systems with new AI capabilities without
compromising stability. When they review the code quality and structural integrity of my
working RAG project, the single action I want them to take is to DM me on LinkedIn to
discuss an open senior engineering role.
"

## Honest Why
"A standard CV lists history and buzzwords, but fails to prove that a veteran engineer can write and deploy functional, production-ready AI code from scratch today."

## Tutor Instructions
- Act as a candid technical tutor across this build.
- Challenge unnecessary complexity and emphasize enterprise code quality & stability.

## Two-Line Style Note (Identity Kit)
- Fonts: Inter (Headings 700, Body 400), JetBrains Mono (Tech Badges). Palette: Accent #0284c7, Text #0f172a, BG #f8fafc, Border #e2e8f0.
- Mood: Calm precision engineering framing that lets hard technical proof speak loudest without competing visual clutter.

## Repository overview

This repo holds a series of independent Flyrank backend assignments, each in its own top-level directory. Each assignment is self-contained (own dependencies, own `.gitignore`) and builds on the previous one — read the earlier assignment before modifying a later one that says it extends it.

- `BE-01-FastAPI/` — assignment BE-01. A minimal single-file FastAPI service (`main.py`) with `POST /user` and `GET /user/{user_id}`, backed by an in-memory dict. No database, no persistence across restarts.
- `BE-04-Containerize/` — assignment BE-04. Takes BE-01 and upgrades it to a layered, containerized service backed by PostgreSQL, with Liquibase-managed migrations, plus a new `Task` domain (assignment/status lifecycle). This is the actively developed project; BE-01 is left as-is as a historical reference.
- `FL-03-Sitemap/` — not a code project. Design/planning deliverable (portfolio sitemap + Claude Project setup write-up) for `portfolio.taskmind-ai.com`. No dependencies, build, or tests — see the dedicated section below.

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

- `POST /task` — create with `name` (mandatory) plus `description`, `estimated_duration_days` (optional). `start_date`/`end_date` and status/assignee are not accepted here and always default.
- `PATCH /task/{task_id}` — metadata only (`name`, `description`, `estimated_duration_days`). `start_date`/`end_date` are **not** patchable — see below.
- `PATCH /task/{task_id}/assignee` — assign a `PLANNED` task, or reassign an already-`ASSIGNED` task to a different user. Touches only `assignee_user_id`/`status`, never `start_date`/`end_date`. `409` if the task is `STARTED`/`FAILED`/`DONE` — deassign first.
- `DELETE /task/{task_id}/assignee` — deassign a single task only (does not touch the rest of that user's assignments).
- `PATCH /task/{task_id}/status` — status transition only. This is the **sole** place `start_date`/`end_date` are ever set.

Allowed transitions: `PLANNED → ASSIGNED → STARTED → DONE`, `STARTED → FAILED`, `FAILED → STARTED`. An invalid transition returns `409 Conflict` with a business-rule message — do not let routes or repositories bypass this check.

`start_date`/`end_date` are business-process-owned, not client-editable metadata — this was a real design bug that got fixed (see Gotchas): `-> STARTED` sets `start_date` to now and clears `end_date` (covers both the first `ASSIGNED -> STARTED` move and a `FAILED -> STARTED` retry); `-> DONE`/`-> FAILED` sets `end_date` to now; `-> ASSIGNED` sets neither. `TaskService.change_status` is the only place that writes these fields going forward — do not let `update_task`, `assign_task`, or any route accept them again.

A task has a single current `assignee_user_id`. Deassigning (single-task `DELETE .../assignee` or bulk `POST /users/{user_id}/tasks/unassign`) resets a `PLANNED`/`ASSIGNED`/`STARTED`/`FAILED` task back to `PLANNED`, clearing `assignee_user_id`/`start_date`/`end_date`. A `DONE` task is the deliberate exception: it's treated as a historical record, not an active assignment — deassigning it only clears `assignee_user_id`, while `status`, `start_date`, and `end_date` are all preserved. `TaskService.assign_task`/`unassign_task` enforce this; do not let a route or the bulk path bypass it. `UserTaskService.has_assigned_tasks` (which gates `DELETE /user/{user_id}` with `409`) and the bulk unassign loop both count only *active* (non-`DONE`) assignments — a user who only owns `DONE` tasks can be deleted directly. That's safe because the `tasks.assignee_user_id` FK (`fk_tasks_assignee_user`, changeset `004_task_assignee_fk_on_delete_set_null.sql`) is `ON DELETE SET NULL`, so deleting such a user automatically nulls the reference on their completed tasks instead of erroring or requiring a prior cleanup step.

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
- Replaying the real changesets is deliberate: it's what caught (and, in `tests/integration/test_task_api.py::test_get_task_includes_start_and_end_date`, still guards) drift between `models.py` and the migration files — see the Gotchas note on changeset 003 below.

### Gotchas

- `models.py`'s `Task` model and the migrations that create the `tasks` table can drift silently if a new column is added to one but not the other — changeset `002_create_tasks_tables.sql` originally didn't create `assigned_at`/`started_at`/`finished_at`/`failed_at`, which `models.py` already declared; this surfaced as a `psycopg2.errors.UndefinedColumn` at insert time. Fixed via a new changeset (`003_add_task_lifecycle_timestamps.sql`) — never edit an already-applied changeset in place, since Liquibase checksum-validates them; always add a new one. (Those four columns were later dropped entirely — see the next Gotcha — but the "add a new changeset, never edit one in place" rule still applies to every schema change, including that removal, which is changeset `005`.)
- Those `assigned_at`/`started_at`/`finished_at`/`failed_at` columns turned out to be a design mistake in their own right: `start_date`/`end_date` already existed as a second, independently-editable pair of task dates, so the table carried two parallel mechanisms for the same concept — one client-editable via `PATCH`, one business-process-driven. Resolved by dropping the `*_at` quartet (changeset `005_drop_task_lifecycle_at_columns.sql`) and making `start_date`/`end_date` the sole date fields, set exclusively by `TaskService.change_status` (see the Task lifecycle section above). If you're ever tempted to add a task date field, first check whether `start_date`/`end_date` can already express it — a second date pair is exactly how this mistake happened the first time.
- Changing Postgres credentials in `.env` does not take effect against an existing volume — run `docker compose down -v` then bring `db` back up before re-migrating.
- If `web` can't find tables, check that `db-migrate` actually completed (`docker compose up --build db-migrate`) before assuming an app-level bug.
- `UserTaskService.has_assigned_tasks` and the bulk-unassign loop must keep excluding `DONE` tasks — treating a completed task as an "active assignment" would either permanently block deleting anyone who ever finished a task, or silently reset that task back to `PLANNED` and erase `end_date` just to unblock the delete. If the FK on `tasks.assignee_user_id` is ever changed away from `ON DELETE SET NULL`, this logic needs to be revisited together, since they were designed as a pair.

---

## FL-03-Sitemap

This directory is a design/planning deliverable, not a codebase — there is nothing to build, lint, or test here.

- `sitemap_submission.md` — the actual submission: positioning/proof statement, a 4-page portfolio sitemap (`/`, `/work`, `/about`, LinkedIn DM as the single conversion action) for `portfolio.taskmind-ai.com`, the custom instructions pasted into a dedicated Claude Project used to pressure-test the sitemap, and the resulting refinement (pin an "Enterprise RAG & Infrastructure" filter at the top of the site; demote casual side projects to a secondary "Explorations" section).
- `sitemap_sketch.excalidraw` / `sitemap_sketch.png` — the Excalidraw canvas behind the sitemap diagram referenced in the submission doc, and its exported image.
- `claude_project_screenshot.png` — screenshot of the configured Claude Project referenced in the submission doc.

Note: `sitemap_submission.md` titles itself "FL-01 Assignment" even though the directory is named `FL-03-Sitemap`, and its Excalidraw file links point at a sibling `Fl-01-Workflow-Audit/` path rather than this directory. If asked to edit this deliverable, confirm with the user which assignment number/location is authoritative before renaming or moving anything.
