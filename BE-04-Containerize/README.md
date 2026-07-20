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

## 4. Directory & File Catalog

```text
BE-04-Containerize/
├── db/
│   └── changelog/
│       ├── db.changelog-master.xml             # Main Liquibase migration schema entrypoint
│       └── changesets/
│           └── 001_create_users_table.sql      # Formatted SQL changeset to create "users" table
├── .env                                        # Environment variables for dev (git-ignored)
├── .env.example                                # Template for required environment variables
├── .gitignore                                  # Standard Git ignores (cache, venv, secrets)
├── config.py                                   # Pydantic Settings class for app configurations
├── database.py                                 # SQLAlchemy engine creation & session dependency
├── Dockerfile                                  # Docker image definition for the FastAPI application
├── docker-compose.yml                          # Container orchestration configuration
├── main.py                                     # FastAPI routers, exception handlers, and endpoint logic
├── models.py                                   # SQLAlchemy Declarative model defining database schema
├── README.md                                   # This documentation file
├── requirements.txt                            # App dependencies manifest
└── schemas.py                                  # Pydantic schemas validating API requests & responses
```

---

## 5. Installation & Setup

### Option A: Running with Docker Compose (Recommended)

To run the entire stack (FastAPI API, PostgreSQL database, and Liquibase migrator), you only need Docker installed:

1. **Clone and Navigate to the Directory**:
   ```bash
   cd BE-04-Containerize
   ```
2. **Build and Run the Containers**:
   ```bash
   docker compose up --build
   ```
3. **What happens under the hood**:
   - The `db` container starts up PostgreSQL.
   - The `db-migrate` container waits for PostgreSQL to become healthy, runs Liquibase to apply migrations, and then exits.
   - The `web` container builds the FastAPI app, waits for migrations to complete, verifies health, and starts Uvicorn on port `8000`.

---

### Option B: Local Running (No Docker - API Only)

If you have a local PostgreSQL instance running and want to run the FastAPI server directly on your host machine:

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
   Copy `.env.example` to `.env` and change `POSTGRES_HOST` to your database address (e.g. `localhost`):
   ```env
   POSTGRES_USER=postgres
   POSTGRES_PASSWORD=postgrespassword
   POSTGRES_DB=user_db
   POSTGRES_HOST=localhost
   POSTGRES_PORT=5432
   ```
4. **Run the Application**:
   ```bash
   uvicorn main:app --reload
   ```

---

## 6. API Usage Guide

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

### 3. Retrieve a User by ID
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

### 4. Create a User (Error: Extra parameters)
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
