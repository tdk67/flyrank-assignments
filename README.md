# Flyrank Backend Assignments

A sequence of backend engineering assignments for Flyrank. Each one is a self-contained project in its own directory, and each builds on the lessons of the previous one. See [CLAUDE.md](CLAUDE.md) for setup commands and detailed architecture notes; each assignment also has its own README with full instructions.

## BE-01 — FastAPI User Service

Directory: [BE-01-FastAPI/](BE-01-FastAPI/)

**Problem statement**: build a minimal backend service exposing two endpoints — create a user and retrieve a user by id — with strict input validation (reject unknown fields, missing required fields, malformed email) and clear, readable error messages. No persistence requirement; the goal was to prove the API contract, not survive a restart.

**Solution**: a single-file FastAPI app (`main.py`). Pydantic models with `ConfigDict(extra="forbid")` enforce the strict validation; a plain Python `dict` acts as the in-memory user store; `POST /user` and `GET /user/{user_id}` implement the two endpoints; a custom `RequestValidationError` handler collapses Pydantic's structured error list into a single readable `detail` string (e.g. `"name: Field required"`). Swagger and ReDoc docs are generated automatically from the type annotations, no extra setup needed.

## BE-04 — Persistent & Containerized User/Task Service

Directory: [BE-04-Containerize/](BE-04-Containerize/)

**Problem statement**: take the BE-01 service and prove that its data survives a restart. Run Postgres in Docker with a volume, connect the app to it by swapping the in-memory store for a real repository *without changing the service or route layers*, put the connection string in a gitignored `.env` (with a committed `.env.example`), define the schema with a SQL migration, and start the whole stack — app plus database — with one `docker compose up`. Persistence has to be demonstrated across an app-and-container restart, and how it was checked has to be documented honestly in the README.

**Solution**: the persistence goal was met by introducing a layered, port/adapter architecture — `api/routes` → `services` → a `*_repository_port.py` interface → a SQLAlchemy-backed repository → PostgreSQL — so the in-memory-to-Postgres swap really did touch only the repository layer, as required. Schema changes are managed as versioned SQL changesets applied automatically by Liquibase, run as a `db-migrate` step in `docker-compose.yml` before the API container starts. A `/health` endpoint pings the database so Compose can gate readiness on a real connection, not just process liveness.

The implementation grew past the original persistence-only brief into a small second domain: full `Task` management with an assignment workflow and an explicit status lifecycle (`PLANNED → ASSIGNED → STARTED → DONE`, with a `FAILED` branch), enforced as a state machine in `TaskService` rather than left as free-form field updates. A `UserTaskService` coordinates the two domains — for example, blocking user deletion while the user still has assigned tasks — so `UserService` itself never has to know the task domain exists.

The project also has a pytest suite (`tests/`): unit tests exercise the services against in-memory fakes of the repository ports, and integration tests exercise the real HTTP API against a dedicated test database whose schema is built by replaying the actual Liquibase changesets, not by regenerating it from the ORM models — so the tests can't be fooled by drift between the two.
