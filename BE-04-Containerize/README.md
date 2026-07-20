# BE-04-Containerize: Persistent & Containerized User Service

*Flyrank assignment BE-04*

This project upgrades the in-memory FastAPI backend (`BE-01-FastAPI`) into a production-ready, containerized microservice backed by a persistent PostgreSQL database, with schema migrations managed by Liquibase.

---

## 1. The Problem

In `BE-01-FastAPI`, the application was designed with several limitations:
1. **Volatile Storage**: All user records were kept in a standard Python dictionary in-memory. If the server process crashed, restarted, or updated, all user data was permanently lost.
2. **Concurrency & Scaling Issues**: Because state was held in-memory, running multiple Uvicorn worker processes or scaling out to multiple containers meant user records created on one worker were completely inaccessible on others.
3. **Environment Lock-in**: Installing dependencies manually on host machines is prone to configuration drift ("works on my machine" syndrome).

---

## 2. The Solution

This project transitions the application into a containerized, decoupled architecture:
- **Persistent Database**: Moved the data layer to **PostgreSQL**.
- **Automated Database Migrations**: Integrated **Liquibase** to manage database schema updates. Before the FastAPI app begins accepting requests, Liquibase runs in a dedicated transient container, applying SQL changesets and tracking version state in the database.
- **Decoupled API Contract**: Kept Pydantic validation schemas separated from database Models using **SQLAlchemy 2.0**. This allows developers to tweak API requests/responses (e.g. nested objects) without triggering database refactoring.
- **Health Check & Self-Healing**: Implemented a `/health` check endpoint that pings the database. This endpoint is used by Docker Compose to verify that the container is fully ready to process traffic.
- **Container Orchestration**: Packaged everything into Docker containers managed by a single `docker-compose.yml` file.

---

## 3. Libraries & Tools Used

| Library/Tool | Purpose |
| :--- | :--- |
| **FastAPI** | High-performance API framework to construct endpoints and generate Swagger UI documentation. |
| **Uvicorn** | ASGI server to run the FastAPI application. |
| **SQLAlchemy 2.0** | Object-Relational Mapper (ORM) to manage connections, pool sessions, and interact with PostgreSQL tables. |
| **Psycopg2-binary** | PostgreSQL driver for Python. |
| **Pydantic v2** | Handles request validation, type checking, and response serialization. |
| **Pydantic Settings** | Loads configurations and database credentials from `.env` files and system environment variables. |
| **Liquibase** | Java-based database migration utility (run via Docker) to track, version, and deploy database changes. |

---

## 4. Project Structure and Architecture

The project is now organized around a small layered architecture so the HTTP layer stays thin and the business rules live in the service layer.

```text
BE-04-Containerize/
|-- api/
|   `-- routes/
|       |-- health_routes.py                  # database health endpoint
|       |-- task_routes.py                    # task HTTP handlers
|       `-- user_routes.py                    # user HTTP handlers
|-- db/
|   `-- changelog/
|       |-- db.changelog-master.xml           # Liquibase master changelog
|       `-- changesets/
|           |-- 001_create_users_table.sql                    # users table migration
|           |-- 002_create_tasks_tables.sql                   # tasks + prerequisites migration
|           |-- 003_add_task_lifecycle_timestamps.sql         # historical *_at columns (see 005)
|           |-- 004_task_assignee_fk_on_delete_set_null.sql   # assignee FK: ON DELETE SET NULL
|           `-- 005_drop_task_lifecycle_at_columns.sql        # drops the columns 003 added
|-- dtos/
|   |-- task_dto.py                           # internal task DTOs
|   `-- user_dto.py                           # internal user DTOs
|-- repositories/
|   |-- task_repository.py                    # SQLAlchemy task persistence adapter
|   |-- task_repository_port.py               # task repository interface
|   |-- user_repository.py                    # SQLAlchemy user persistence adapter
|   `-- user_repository_port.py               # user repository interface
|-- services/
|   |-- service_factories.py                  # route-to-service construction helpers
|   |-- task_service.py                       # task state machine and business rules
|   |-- user_service.py                       # user CRUD business rules
|   `-- user_task_service.py                  # cross-domain assignment / unassign / delete safety
|-- .env                                       # developer-local secrets (git ignored)
|-- .env.example                               # environment template
|-- config.py                                  # application settings and DSN assembly
|-- database.py                                # SQLAlchemy engine / session dependency
|-- docker-compose.yml                         # app + DB + migration orchestration
|-- Dockerfile                                 # FastAPI runtime image
|-- main.py                                    # composition root and router registration
|-- migrate.Dockerfile                          # Liquibase image with PostgreSQL JDBC driver
|-- models.py                                  # SQLAlchemy ORM models
|-- PRD.md                                     # product requirements / design notes
|-- README.md                                  # this documentation file
|-- requirements.txt                           # runtime dependencies
|-- schemas.py                                 # Pydantic request/response schemas
`-- task-BE-04.txt                             # assignment task notes
```

---

## 4.1 Architecture Notes

The implementation follows a layered, service-oriented style:

- `main.py` is the composition root. It creates the FastAPI application and registers the route modules.
- `api/routes/*.py` contains only HTTP concerns: request parsing, response serialization, and status-code handling.
- `services/*.py` contains the business behavior. This is where the task lifecycle rules, assignment policy, and deletion-safety logic live.
- `repositories/*.py` are the database adapters. They know how to persist and query the ORM models using SQLAlchemy.
- `dtos/*.py` are internal transport objects that keep the domain layer separate from both the HTTP schemas and the ORM models.
- `schemas.py` is the API contract layer. It validates client input and shapes the JSON response model.
- `models.py` is the persistence model layer. It describes the database tables and their relationship columns.

This separation matters because it prevents the route layer from becoming a place where business policy is hidden. The API stays thin, while the service layer owns the process rules.

### Current responsibility split

- `UserService` handles user CRUD and user lookup logic.
- `TaskService` handles task creation, metadata update, status transitions, and assignment lifecycle rules.
- `UserTaskService` coordinates cross-domain user/task decisions such as assignment checks and unassignment cleanup.

That last part is important for the delete workflow: the user service should not need to know about the task domain in order to decide whether a user can be deleted.

### Current task lifecycle design

The task lifecycle is intentionally explicit and narrow. The API is split into dedicated actions instead of letting one generic patch endpoint overload too many meanings.

- `POST /task` creates a task from `name` (mandatory) plus optional `description` and `estimated_duration_days`. `start_date`/`end_date` and status/assignee are never accepted here - every task date is set exclusively by the status transitions below, never by a client.
- `PATCH /task/{task_id}` updates task metadata: `name`, `description`, `estimated_duration_days` only. `start_date`/`end_date` are **not** patchable - they're owned entirely by `PATCH /task/{task_id}/status` (see below).
- `PATCH /task/{task_id}/assignee` assigns or reassigns a task to a user - nothing else.
- `DELETE /task/{task_id}/assignee` deassigns a single task - nothing else.
- `PATCH /task/{task_id}/status` performs the state transition only.

The status machine is enforced in the service layer:

- `PLANNED -> ASSIGNED`
- `ASSIGNED -> STARTED`
- `STARTED -> DONE`
- `STARTED -> FAILED`
- `FAILED -> STARTED`

Invalid transitions return a `409 Conflict` with a business-rule message rather than silently mutating state.

`start_date`/`end_date` are set exclusively by these transitions, never by a client: `start_date` is stamped on `-> STARTED` (covering both the first `ASSIGNED -> STARTED` move and a `FAILED -> STARTED` retry, which also clears `end_date` since the task is active again), and `end_date` is stamped on `-> DONE` or `-> FAILED`. Moving to `ASSIGNED` sets no date - assignment itself isn't "the clock starting," actual work starting is. There used to be a separate quartet of `assigned_at`/`started_at`/`finished_at`/`failed_at` columns doing this same job in parallel with `start_date`/`end_date`; they were dropped (changeset `005_drop_task_lifecycle_at_columns.sql`) because two independently-settable date pairs tracking the same lifecycle was the actual design mistake - `start_date`/`end_date` are now the single source of truth for "when did this task's status last enter an active/terminal state."

### User-task assignment and delete safety

The project uses a single current assignee per task. That means the task table keeps one `assignee_user_id` reference, which is the current owner of the task.

Assignment has both a single-task and a bulk path:

1. `PATCH /task/{task_id}/assignee` assigns a `PLANNED` task, or **reassigns** an already-`ASSIGNED` task to a different user. It only ever touches `assignee_user_id`/`status` - it never sets `start_date`/`end_date`, since assignment isn't when the clock starts (see above). A `STARTED` or `FAILED` task must be deassigned first - reassigning in-flight work is a deliberate two-step action, not a silent swap.
2. `DELETE /task/{task_id}/assignee` deassigns a single task, dropping it back to `PLANNED` and clearing `start_date`/`end_date` - **except** for a `DONE` task, where only the owner link (`assignee_user_id`) is cleared; `status`, `start_date`, and `end_date` are all preserved as a historical completion record.
3. `POST /users/{user_id}/tasks/unassign` is the bulk equivalent of (2) applied to every **active** (non-`DONE`) task a user holds - the cleanup step before deleting a user. It intentionally skips `DONE` tasks: their completion record isn't an active assignment to clear.
4. `DELETE /user/{user_id}` is rejected with `409` while the user still holds an active (`PLANNED`/`ASSIGNED`/`STARTED`/`FAILED`) assignment. A user who only owns `DONE` tasks can be deleted directly - those tasks keep their `status`, `start_date`, and `end_date`, and the FK (`fk_tasks_assignee_user`, `ON DELETE SET NULL` as of changeset `004`) automatically nulls out `assignee_user_id` on delete.

This avoids hidden data corruption and keeps the API behavior predictable: a delete never silently orphans an active assignment, and finishing a task doesn't create a permanent dependency between that user and the task record.

### Why this structure was chosen

This architecture was deliberately kept small but extensible:

- it separates transport concerns from persistence concerns
- it allows new task rules to be added in one service place
- it keeps the route layer thin and easier to reason about
- it makes future task prerequisites, auditing, pagination, and search easier to evolve without changing the HTTP entrypoints unnecessarily

---

## 5. API Reference

### 5.1 Overview

The API exposes two resource domains that together model "who can do work" and "what work needs doing":

- **Users** (`/user`, `/users`) are the people who can be assigned work. User endpoints cover plain CRUD plus filtered lookup.
- **Tasks** (`/task`, `/tasks`) are units of work that move through a status lifecycle (`PLANNED -> ASSIGNED -> STARTED -> DONE`, with a `STARTED <-> FAILED` branch). Task endpoints are deliberately split into narrow, single-purpose actions - create, metadata update, assignee update, status update - rather than one generic PATCH, so each action can carry its own validation rules.
- **Assignment** is the bridge between the two domains. `PATCH /task/{task_id}/assignee` links a task to a user - moving a `PLANNED` task to `ASSIGNED`, or reassigning an already-`ASSIGNED` task to someone else. `DELETE /task/{task_id}/assignee` is the single-task inverse: it deassigns one task without touching the rest of that user's work. `POST /users/{user_id}/tasks/unassign` is the bulk version of the same deassign, applied to every *active* task a user holds, and exists specifically to unblock user deletion: `DELETE /user/{user_id}` returns `409 Conflict` while the user still holds an active (non-`DONE`) assignment. A `DONE` task is treated as a historical record rather than an active assignment - it never blocks deletion, and deassigning it (individually, in bulk, or by deleting its owner) clears only the owner link while `status`, `start_date`, and `end_date` stay intact. This logic - and the assignment/reassignment rules themselves - lives in `UserTaskService` and `TaskService`, coordinating across both domains without either `UserService` needing to know about tasks.
- **Dates** (`start_date`/`end_date`) are never client-settable, at creation or via `PATCH` - they're stamped exclusively by `PATCH /task/{task_id}/status` (`start_date` on `-> STARTED`, `end_date` on `-> DONE`/`-> FAILED`), and cleared by deassignment. This is deliberate: dates are an audit trail of the state machine, not free-form metadata.

Together, these endpoints let a client fully maintain the user roster, maintain the task backlog, and drive the assignment relationship between them, while the service layer guarantees the system never ends up in an inconsistent state (an orphaned assignment, a deleted user with live tasks, or an illegal status jump).

### 5.2 Endpoints

| Method | Path | Description |
| :--- | :--- | :--- |
| `GET` | `/health` | Health check; pings the database and reports connectivity. |
| `POST` | `/user` | Create a new user. |
| `GET` | `/users` | List users, optionally filtered by `email`, `first_name`, `last_name`, or `telephone`. |
| `GET` | `/user/{user_id}` | Retrieve a single user by id. |
| `PATCH` | `/user/{user_id}` | Partially update a user's name, email, and/or telephone; omitted fields are left unchanged. |
| `DELETE` | `/user/{user_id}` | Delete a user. Rejected with `409` if the user still holds an active (non-`DONE`) task assignment. |
| `POST` | `/users/{user_id}/tasks/unassign` | Deassign every active task a user holds, resetting each back to `PLANNED`. `DONE` tasks are left untouched. |
| `POST` | `/task` | Create a new task from `name` (mandatory), `description`, `estimated_duration_days`; `start_date`/`end_date` and status/assignee always default. |
| `GET` | `/tasks` | List tasks, optionally filtered by `assignee_user_id`, `status`, or `name`. |
| `GET` | `/task/{task_id}` | Retrieve a single task by id. |
| `PATCH` | `/task/{task_id}` | Update task metadata (`name`, `description`, `estimated_duration_days`). `start_date`/`end_date` are not patchable - set exclusively by status transitions. |
| `PATCH` | `/task/{task_id}/assignee` | Assign a `PLANNED` task, or reassign an `ASSIGNED` task to a different user. `409` if the task is `STARTED`, `FAILED`, or `DONE`. |
| `DELETE` | `/task/{task_id}/assignee` | Deassign a single task. Resets to `PLANNED` (clearing `start_date`/`end_date`) - except a `DONE` task, where only the owner link is cleared and `status`/`start_date`/`end_date` are preserved. |
| `PATCH` | `/task/{task_id}/status` | Transition a task's status through the lifecycle state machine. Invalid transitions return `409`. |
| `DELETE` | `/task/{task_id}` | Delete a task. |

Full request/response schemas are available interactively via Swagger UI (`/docs`) or ReDoc (`/redoc`) once the server is running; worked `curl` examples for the endpoints above are in [Section 9, API Usage Guide](#9-api-usage-guide).

---

## 6. Installation & Setup

### Option A: Running with Docker Compose (Recommended)

To run the entire stack (FastAPI API, PostgreSQL database, and Liquibase migrator), you only need Docker installed:

1. **Clone and Navigate to the Directory**:
   ```bash
   cd BE-04-Containerize
   ```
2. **Create a local `.env` file** from the template:
   ```bash
   cp .env.example .env
   ```
   The `.env` file is the local source of truth for Postgres credentials and should never be committed.
3. **Start the database and migration-backed application**:
   ```bash
   docker compose up --build
   ```
4. **What happens under the hood**:
   - The `db` container starts PostgreSQL with the values from `.env`.
   - The `db-migrate` container waits for Postgres to become healthy, runs Liquibase, and applies the SQL changeset.
   - The `web` container builds the FastAPI app, waits for migrations to complete, and starts Uvicorn on port `8000`.

> If you change the username or password in `.env`, the old database state can persist because the Postgres data volume is reused. To fully reset that credential state, run:
> ```bash
> docker compose down -v
> docker compose up -d db
> ```

---

### Option B: Local Running (No Docker - API Only)

If you want to run the FastAPI server directly on your host machine and connect to the Dockerized PostgreSQL container:

1. **Create and Activate a Virtual Environment**:
   ```bash
   python -m venv .venv
   # Windows:
   .venv\Scripts\activate
   # macOS/Linux:
   source .venv/bin/activate
   ```
2. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```
3. **Configure Environment**:
   Copy `.env.example` to `.env` and set `POSTGRES_HOST=localhost` for the local app:
   ```env
   POSTGRES_USER=postgres
   POSTGRES_PASSWORD=postgrespassword
   POSTGRES_DB=user_db
   POSTGRES_HOST=localhost
   POSTGRES_PORT=5432
   ```
4. **Run the Database Container Only**:
   ```bash
   docker compose up -d db
   ```
5. **Run the Application Locally**:
   ```bash
   source .venv/bin/activate
   uvicorn main:app --host 127.0.0.1 --port 8000 --reload
   ```

This local run path is useful for debugging the API while the DB remains in Docker.

---

## 6.1 Secrets and Environment Variables

The project now reads Postgres credentials from environment variables instead of storing them directly in the Compose file.

- Safe local secret source: `.env`
- Shared template: `.env.example`
- Git ignore rule: `.env`

Recommended pattern:

```yaml
environment:
  POSTGRES_USER: ${POSTGRES_USER}
  POSTGRES_PASSWORD: ${POSTGRES_PASSWORD}
  POSTGRES_DB: ${POSTGRES_DB}
```

This keeps credentials out of Git while still allowing a project-local developer setup.

If you use a different username or password than the defaults, set them in `.env` and restart the stack from a clean DB state if needed.

### URL-escaping password characters

The database connection string is assembled in `config.py` by combining the Postgres username, password, host, port, and database name into a URI.

If the password contains reserved URI characters such as `@`, `!`, `*`, `%`, `:`, `/`, or `?`, they must be percent-encoded before being placed into the URL. Otherwise the DSN parser may misread the host and produce errors like:

```text
could not translate host name "xyz@localhost" to address
```

The safe pattern is:

```python
from urllib.parse import quote_plus

user = quote_plus(settings.postgres_user)
password = quote_plus(settings.postgres_password)
url = f"postgresql://{user}:{password}@{settings.postgres_host}:{settings.postgres_port}/{settings.postgres_db}"
```

This is an important real-world lesson: credentials are often user-supplied data, and they must be treated as untrusted input when building a connection string.

---

## 7. Testing

The test suite lives under `tests/` and is split into two layers that trade off speed against fidelity to production.

### 7.1 Test layout

```text
tests/
|-- conftest.py                    # test-DB creation, migration replay, transactional session, TestClient override
|-- unit/
|   |-- fakes.py                   # in-memory fakes of UserRepositoryPort / TaskRepositoryPort
|   |-- test_user_service.py
|   |-- test_task_service.py
|   `-- test_user_task_service.py
|-- integration/
|   |-- conftest.py                # sample-data loading fixture
|   |-- sample_data.py             # named UUID constants for the fixture data
|   |-- test_health_api.py
|   |-- test_user_api.py
|   `-- test_task_api.py
`-- fixtures/
    `-- sample_data.json           # the sample dataset: 3 users, 4 tasks across the status lifecycle
```

### 7.2 Unit tests

`tests/unit/` tests `UserService`, `TaskService`, and `UserTaskService` in isolation, against hand-written in-memory fakes of the repository ports (`tests/unit/fakes.py`) rather than a real database. No network, no Docker, no migrations - these run in well under a second and are the fast feedback loop for changes to business rules (the status state machine, assignment/unassignment, delete-safety).

### 7.3 Integration tests

`tests/integration/` exercises the real HTTP surface end-to-end:

1. **Schema**: a session-scoped fixture drops and recreates a dedicated `user_db_test` database on the same Postgres container the dev stack already runs, then replays the actual Liquibase changeset files from `db/changelog/changesets/` in order - not `Base.metadata.create_all()` from `models.py`. This is deliberate: replaying the real migration files is what would have caught (and still guards against) drift between `models.py` and the changesets, such as the missing `assigned_at` / `started_at` / `finished_at` / `failed_at` columns that changeset `002_create_tasks_tables.sql` originally omitted.
2. **Sample dataset**: `tests/fixtures/sample_data.json` defines a fixed dataset - Ada, Alan, and Grace as users, and four tasks spanning the full status lifecycle (`PLANNED`, `ASSIGNED`, `STARTED`, `DONE`). The `seeded_db` fixture (`tests/integration/conftest.py`) inserts this dataset directly via the SQLAlchemy session before each test that requests it; `tests/integration/sample_data.py` exposes the same IDs as named constants (`ADA_ID`, `TASK_SHIP_RELEASE_ID`, ...) so tests read like prose instead of scattering raw UUID strings.
3. **Isolation**: each test runs inside its own database transaction, opened before the test and rolled back after (see the `db_session` fixture in `tests/conftest.py`). Repositories call `session.commit()` during normal request handling; an `after_transaction_end` listener restarts a SAVEPOINT whenever that happens, so those commits only release the savepoint - nothing survives past the test.
4. **Driving the API**: the `client` fixture overrides the `get_db` FastAPI dependency to yield that same per-test session, then wraps the app in `TestClient`, so requests exercise the real routes, services, and repositories - the only thing swapped out is which database transaction they talk to.

### 7.4 Running the tests

```bash
docker compose up -d db              # only the db container needs to be running
pip install -r requirements-dev.txt  # adds pytest and httpx on top of requirements.txt
pytest
```

Expected output:
```text
64 passed in ~1s
```

Run just one layer, one file, or one test:
```bash
pytest tests/unit                                            # fast, no DB
pytest tests/integration/test_task_api.py -v
pytest tests/integration/test_task_api.py::test_invalid_status_transition_rejected
```

`pytest.ini` sets `pythonpath = .`, so tests can import app modules directly (`from services.user_service import UserService`, `from database import get_db`, etc.) regardless of the shell's working directory when `pytest` is invoked.

---

## 8. Troubleshooting

### 1. `Cannot find database driver: org.postgresql.Driver`

This error comes from the `db-migrate` container. The upstream `liquibase/liquibase:latest` image does not include the PostgreSQL JDBC driver in a reliable way for this project.

The fix used here is a custom migration image with the PostgreSQL JDBC jar added explicitly via `migrate.Dockerfile`.

If you see this error:

```text
Cannot find database driver: org.postgresql.Driver
```

rebuild the migrator image and rerun it:

```bash
docker compose build db-migrate
docker compose up --build db-migrate
```

---

### 2. `relation "users" does not exist`

This means the FastAPI app connected to the Postgres container successfully, but the schema migration did not apply the `users` table.

Check the DB schema:

```bash
docker exec -it user_service_db psql -U postgres -d user_db -c '\dt'
```

If the table is missing:

```bash
docker compose up --build db-migrate
```

If the migration still fails, rebuild the migrator image again and inspect the log output.

---

### 3. `Address already in use` when starting `uvicorn`

This means a previous backend process is still holding port `8000`.

Check for the old process:

```bash
ps -ef | grep uvicorn
```

Or inspect the port directly:

```bash
lsof -i :8000
```

Then stop the stale process:

```bash
kill <PID>
```

Now restart the app:

```bash
source .venv/bin/activate
uvicorn main:app --host 127.0.0.1 --port 8000 --reload
```

---

### 4. Username/password changes do not take effect

Postgres keeps its database state in a Docker volume. If you change the credentials in `.env` and restart the container, the old database user state may still remain.

To reset the whole database state:

```bash
docker compose down -v
docker compose up -d db
```

After that, rerun the migration and restart the API.

---

## 9. API Usage Guide

Once the server is running, the Swagger interactive documentation is accessible at:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

### 1. Perform a Health Check
Verify the API is healthy and connected to the database:
```bash
curl -i http://localhost:8000/health
```
*Expected response (`200 OK`)*:
```json
{"status": "healthy", "database": "connected"}
```

### 2. Create a User (Success)
Send a POST request with the mandatory `name` parameters:
```bash
curl -i -X POST http://localhost:8000/user \
  -H "Content-Type: application/json" \
  -d '{"name":{"first_name":"Jane","last_name":"Doe"},"email":"jane.doe@example.com","telephone":"+1-555-0100"}'
```
*Expected response (`201 Created`)*:
```json
{
  "id": "c3b9a7a9-91c6-43b6-9812-a16fbd4c6a6f",
  "name": {"first_name": "Jane", "last_name": "Doe"},
  "email": "jane.doe@example.com",
  "telephone": "+1-555-0100"
}
```

### 3. Create a Task
`name` is the only mandatory field; `description` and `estimated_duration_days` are optional. `start_date`/`end_date` are not accepted at creation - set them later via `PATCH /task/{task_id}` once the task is actually scheduled. Status, assignee, and lifecycle timestamps are never accepted here either - they always default and are owned by the specialized endpoints (`/status`, `/assignee`).

Minimal request:
```bash
curl -i -X POST http://localhost:8000/task \
  -H "Content-Type: application/json" \
  -d '{"name":"Prepare sprint backlog","description":"Draft the backlog for the next sprint"}'
```

*Expected response (`201 Created`)*:
```json
{
  "id": "e4e5c8a4-2429-4f2c-8752-94c7dd7c6851",
  "name": "Prepare sprint backlog",
  "description": "Draft the backlog for the next sprint",
  "status": "PLANNED",
  "estimated_duration_days": null,
  "start_date": null,
  "end_date": null,
  "assignee_user_id": null
}
```

With the optional `estimated_duration_days` set upfront:
```bash
curl -i -X POST http://localhost:8000/task \
  -H "Content-Type: application/json" \
  -d '{"name":"Prepare sprint backlog","description":"Draft the backlog for the next sprint","estimated_duration_days":5}'
```

### 4. Retrieve all users with optional filters
Return all users, or filter by one or more exact-match query parameters:
```bash
curl -i http://localhost:8000/users
curl -i "http://localhost:8000/users?email=jane.doe@example.com"
curl -i "http://localhost:8000/users?first_name=Jane"
curl -i "http://localhost:8000/users?last_name=Doe"
curl -i "http://localhost:8000/users?telephone=+1-555-0100"
```

For values containing reserved URL characters, prefer URL encoding. Swagger handles this automatically in the UI, but when using raw `curl` you should use `--data-urlencode` or escape the value yourself.

Example:
```bash
curl -G --data-urlencode "email=john.doe@example.com" http://localhost:8000/users
```

### 5. Retrieve a User by ID
Fetch user information using the returned UUID:
```bash
curl -i http://localhost:8000/user/c3b9a7a9-91c6-43b6-9812-a16fbd4c6a6f
```
*Expected response (`200 OK`)*:
```json
{
  "id": "c3b9a7a9-91c6-43b6-9812-a16fbd4c6a6f",
  "name": {"first_name": "Jane", "last_name": "Doe"},
  "email": "jane.doe@example.com",
  "telephone": "+1-555-0100"
}
```

### 6. Assign or reassign a task to a user
Use the dedicated assignment endpoint. Only the assignee is sent in the request body. It works on a `PLANNED` task (first assignment) or an already-`ASSIGNED` task (reassignment to a different user) - `STARTED`, `FAILED`, and `DONE` tasks must be deassigned first (see section 7).

```bash
curl -i -X PATCH http://localhost:8000/task/<task_id>/assignee \
  -H "Content-Type: application/json" \
  -d '{"assignee_user_id":"c3b9a7a9-91c6-43b6-9812-a16fbd4c6a6f"}'
```

Expected behavior:
- if the task was `PLANNED`, it moves to `ASSIGNED`; if it was already `ASSIGNED`, it stays `ASSIGNED` under the new owner
- `assignee_user_id` is updated
- `start_date`/`end_date` are untouched - assignment isn't when the clock starts; that's `PATCH /task/{task_id}/status -> STARTED` (see section 8)

Reassigning a task that isn't `PLANNED` or `ASSIGNED` returns `409 Conflict`:
```bash
curl -i -X PATCH http://localhost:8000/task/<started_task_id>/assignee \
  -H "Content-Type: application/json" \
  -d '{"assignee_user_id":"c3b9a7a9-91c6-43b6-9812-a16fbd4c6a6f"}'
```
```json
{
  "detail": "Only a PLANNED or ASSIGNED task can be (re)assigned through the assignment API; unassign a STARTED/FAILED task first"
}
```

### 7. Deassign a single task
This frees up one task without touching any of that user's other assignments (contrast with section 9, which is a bulk per-user operation).

```bash
curl -i -X DELETE http://localhost:8000/task/<task_id>/assignee
```

Expected behavior:
- for a `PLANNED`, `ASSIGNED`, `STARTED`, or `FAILED` task: `status` resets to `PLANNED`, and `assignee_user_id`/`start_date`/`end_date` are all cleared
- for a `DONE` task: only `assignee_user_id` is cleared - `status`, `start_date`, and `end_date` are all preserved, since a completed task's history shouldn't be discarded just because its owner is being detached

### 8. Change task status through the lifecycle
Status changes are validated in the service layer, and `start_date`/`end_date` are stamped here - nowhere else.

```bash
curl -i -X PATCH http://localhost:8000/task/<task_id>/status \
  -H "Content-Type: application/json" \
  -d '{"status":"STARTED"}'
```

Allowed transitions are:
- `PLANNED -> ASSIGNED` - no date change
- `ASSIGNED -> STARTED` - sets `start_date` to now
- `STARTED -> DONE` - sets `end_date` to now
- `STARTED -> FAILED` - sets `end_date` to now
- `FAILED -> STARTED` - a retry: refreshes `start_date` to now and clears `end_date`, since the task is active again

If the transition is invalid, the API returns `409 Conflict` with a clear business-rule message.

### 9. Unassign all of a user's active tasks
This is an explicit bulk cleanup command that resets every task the user is *actively* assigned to (`PLANNED`/`ASSIGNED`/`STARTED`/`FAILED`) back to `PLANNED` and clears `start_date`/`end_date`. `DONE` tasks are left alone - completing a task isn't an active assignment, so there's nothing to unassign; use section 7 if you specifically want to detach a `DONE` task's owner.

```bash
curl -i -X POST http://localhost:8000/users/<user_id>/tasks/unassign
```

Expected response (`200 OK`):
```json
{
  "unassigned_count": 2
}
```

### 10. Delete a user that still has an active task assignment
Deleting a user is blocked when the user still owns an active (non-`DONE`) task assignment. A user who only owns `DONE` tasks can be deleted directly - those tasks keep their `status`, `start_date`, and `end_date`, and `assignee_user_id` is nulled out automatically by the database foreign key.

```bash
curl -i -X DELETE http://localhost:8000/user/<user_id>
```

Expected response (`409 Conflict`):
```json
{
  "detail": "User with id '<user_id>' still has assigned tasks and cannot be deleted until they are unassigned"
}
```

### 11. Create a User (Error: Extra parameters)
Any unexpected request properties (such as `age`) will trigger a strict rejection validation error due to the configured `ConfigDict(extra="forbid")`:
```bash
curl -i -X POST http://localhost:8000/user \
  -H "Content-Type: application/json" \
  -d '{"name":{"first_name":"Jane","last_name":"Doe"},"age":30}'
```
*Expected response (`422 Unprocessable Entity`)*:
```json
{"detail": "age: Extra inputs are not permitted"}
```
