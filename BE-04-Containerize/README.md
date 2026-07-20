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
├── api/
│   └── routes/
│       ├── health_routes.py                  # database health endpoint
│       ├── task_routes.py                    # task HTTP handlers
│       └── user_routes.py                    # user HTTP handlers
├── db/
│   └── changelog/
│       ├── db.changelog-master.xml           # Liquibase master changelog
│       └── changesets/
│           ├── 001_create_users_table.sql    # users table migration
│           └── 002_create_tasks_tables.sql    # tasks + prerequisites migration
├── dtos/
│   ├── task_dto.py                           # internal task DTOs
│   └── user_dto.py                           # internal user DTOs
├── repositories/
│   ├── task_repository.py                    # SQLAlchemy task persistence adapter
│   ├── task_repository_port.py               # task repository interface
│   ├── user_repository.py                    # SQLAlchemy user persistence adapter
│   └── user_repository_port.py               # user repository interface
├── services/
│   ├── service_factories.py                  # route-to-service construction helpers
│   ├── task_service.py                       # task state machine and business rules
│   ├── user_service.py                       # user CRUD business rules
│   └── user_task_service.py                  # cross-domain assignment / unassign / delete safety
├── .env                                       # developer-local secrets (git ignored)
├── .env.example                               # environment template
├── config.py                                  # application settings and DSN assembly
├── database.py                                # SQLAlchemy engine / session dependency
├── docker-compose.yml                         # app + DB + migration orchestration
├── Dockerfile                                 # FastAPI runtime image
├── main.py                                    # composition root and router registration
├── migrate.Dockerfile                          # Liquibase image with PostgreSQL JDBC driver
├── models.py                                  # SQLAlchemy ORM models
├── PRD.md                                     # product requirements / design notes
├── README.md                                  # this documentation file
├── requirements.txt                           # runtime dependencies
├── schemas.py                                 # Pydantic request/response schemas
└── task-BE-04.txt                             # assignment task notes
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

- `POST /task` creates a task with the minimal contract: only `name` and `description` are provided by the client.
- `PATCH /task/{task_id}` updates task metadata only: `name`, `description`, `estimated_duration_days`, `start_date`, `end_date`.
- `PATCH /task/{task_id}/assignee` performs the assignment action only.
- `PATCH /task/{task_id}/status` performs the state transition only.

The status machine is enforced in the service layer:

- `PLANNED -> ASSIGNED`
- `ASSIGNED -> STARTED`
- `STARTED -> DONE`
- `STARTED -> FAILED`
- `FAILED -> STARTED`

Invalid transitions return a `409 Conflict` with a business-rule message rather than silently mutating state.

### User-task assignment and delete safety

The project uses a single current assignee per task. That means the task table keeps one `assignee_user_id` reference, which is the current owner of the task.

This design leads to a clear cleanup workflow:

1. `PATCH /task/{task_id}/assignee` assigns a user to a task.
2. `POST /users/{user_id}/tasks/unassign` explicitly clears assignments for that user and resets the tasks back to `PLANNED`.
3. `DELETE /user/{user_id}` is rejected while the user still has assigned tasks.

This avoids hidden data corruption and keeps the API behavior predictable. A delete does not silently orphan active tasks, and an unassign is intentionally modeled as a first-class business action.

### Why this structure was chosen

This architecture was deliberately kept small but extensible:

- it separates transport concerns from persistence concerns
- it allows new task rules to be added in one service place
- it keeps the route layer thin and easier to reason about
- it makes future task prerequisites, auditing, pagination, and search easier to evolve without changing the HTTP entrypoints unnecessarily

---

## 5. Installation & Setup

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

## 5.1 Secrets and Environment Variables

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

## 6. Testing

The test suite lives under `tests/` and is split into two layers that trade off speed against fidelity to production.

### 6.1 Test layout

```text
tests/
├── conftest.py                    # test-DB creation, migration replay, transactional session, TestClient override
├── unit/
│   ├── fakes.py                   # in-memory fakes of UserRepositoryPort / TaskRepositoryPort
│   ├── test_user_service.py
│   ├── test_task_service.py
│   └── test_user_task_service.py
├── integration/
│   ├── conftest.py                # sample-data loading fixture
│   ├── sample_data.py             # named UUID constants for the fixture data
│   ├── test_health_api.py
│   ├── test_user_api.py
│   └── test_task_api.py
└── fixtures/
    └── sample_data.json           # the sample dataset: 3 users, 4 tasks across the status lifecycle
```

### 6.2 Unit tests

`tests/unit/` tests `UserService`, `TaskService`, and `UserTaskService` in isolation, against hand-written in-memory fakes of the repository ports (`tests/unit/fakes.py`) rather than a real database. No network, no Docker, no migrations — these run in well under a second and are the fast feedback loop for changes to business rules (the status state machine, assignment/unassignment, delete-safety).

### 6.3 Integration tests

`tests/integration/` exercises the real HTTP surface end-to-end:

1. **Schema**: a session-scoped fixture drops and recreates a dedicated `user_db_test` database on the same Postgres container the dev stack already runs, then replays the actual Liquibase changeset files from `db/changelog/changesets/` in order — not `Base.metadata.create_all()` from `models.py`. This is deliberate: replaying the real migration files is what would have caught (and still guards against) drift between `models.py` and the changesets, such as the missing `assigned_at` / `started_at` / `finished_at` / `failed_at` columns that changeset `002_create_tasks_tables.sql` originally omitted.
2. **Sample dataset**: `tests/fixtures/sample_data.json` defines a fixed dataset — Ada, Alan, and Grace as users, and four tasks spanning the full status lifecycle (`PLANNED`, `ASSIGNED`, `STARTED`, `DONE`). The `seeded_db` fixture (`tests/integration/conftest.py`) inserts this dataset directly via the SQLAlchemy session before each test that requests it; `tests/integration/sample_data.py` exposes the same IDs as named constants (`ADA_ID`, `TASK_SHIP_RELEASE_ID`, …) so tests read like prose instead of scattering raw UUID strings.
3. **Isolation**: each test runs inside its own database transaction, opened before the test and rolled back after (see the `db_session` fixture in `tests/conftest.py`). Repositories call `session.commit()` during normal request handling; an `after_transaction_end` listener restarts a SAVEPOINT whenever that happens, so those commits only release the savepoint — nothing survives past the test.
4. **Driving the API**: the `client` fixture overrides the `get_db` FastAPI dependency to yield that same per-test session, then wraps the app in `TestClient`, so requests exercise the real routes, services, and repositories — the only thing swapped out is which database transaction they talk to.

### 6.4 Running the tests

```bash
docker compose up -d db              # only the db container needs to be running
pip install -r requirements-dev.txt  # adds pytest and httpx on top of requirements.txt
pytest
```

Expected output:
```text
49 passed in ~1s
```

Run just one layer, one file, or one test:
```bash
pytest tests/unit                                            # fast, no DB
pytest tests/integration/test_task_api.py -v
pytest tests/integration/test_task_api.py::test_invalid_status_transition_rejected
```

`pytest.ini` sets `pythonpath = .`, so tests can import app modules directly (`from services.user_service import UserService`, `from database import get_db`, etc.) regardless of the shell's working directory when `pytest` is invoked.

---

## 7. Troubleshooting

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

## 8. API Usage Guide

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

### 3. Create a Task (minimal request)
A task is created with only the user-facing fields. All lifecycle defaults are applied by the service layer.

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
  "assigned_at": null,
  "started_at": null,
  "finished_at": null,
  "failed_at": null,
  "assignee_user_id": null
}
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

### 6. Assign a task to a user
Use the dedicated assignment endpoint. Only the assignee is sent in the request body.

```bash
curl -i -X PATCH http://localhost:8000/task/<task_id>/assignee \
  -H "Content-Type: application/json" \
  -d '{"assignee_user_id":"c3b9a7a9-91c6-43b6-9812-a16fbd4c6a6f"}'
```

Expected behavior:
- the task moves from `PLANNED` to `ASSIGNED`
- `assigned_at` is set
- `assignee_user_id` is updated

### 7. Change task status through the lifecycle
Status changes are validated in the service layer.

```bash
curl -i -X PATCH http://localhost:8000/task/<task_id>/status \
  -H "Content-Type: application/json" \
  -d '{"status":"STARTED"}'
```

Allowed transitions are:
- `PLANNED -> ASSIGNED`
- `ASSIGNED -> STARTED`
- `STARTED -> DONE`
- `STARTED -> FAILED`
- `FAILED -> STARTED`

If the transition is invalid, the API returns `409 Conflict` with a clear business-rule message.

### 8. Unassign all a user's tasks
This is an explicit cleanup command that resets all currently assigned tasks for the user back to `PLANNED` and clears assignment timestamps.

```bash
curl -i -X POST http://localhost:8000/users/<user_id>/tasks/unassign
```

Expected response (`200 OK`):
```json
{
  "unassigned_count": 2
}
```

### 9. Delete a user that still has assigned tasks
Deleting a user is blocked when the user still owns active task assignments.

```bash
curl -i -X DELETE http://localhost:8000/user/<user_id>
```

Expected response (`409 Conflict`):
```json
{
  "detail": "User with id '<user_id>' still has assigned tasks and cannot be deleted until they are unassigned"
}
```

### 10. Create a User (Error: Extra parameters)
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
