# Task API with SQLite (BE-02)

A lightweight FastAPI backend that manages a to-do task list backed by a persistent **SQLite** database. 

This project transitions an in-memory CRUD API into a disk-persisted database service where data survives server restarts, without changing the external API contract.

---

## 🎯 Why SQLite?

- **Zero Setup & Serverless**: SQLite doesn't require installing or managing a standalone database server (like Postgres or MySQL). The entire database lives in a single local file.
- **Data Persistence**: Storing data on disk in `tasks.db` ensures tasks survive server restarts.
- **Single File Storage**: The database file (`tasks.db`) is automatically created on first startup and ignored by Git (`.gitignore`) so every developer clone starts with a clean database.

---

## 🏗️ Layered Architecture & Separation of Concerns

The project strictly decouples HTTP/API concerns from business logic and database access using a 3-tier architecture:

```
[ HTTP Request ]
       │
       ▼
┌──────────────────────┐
│     main.py          │  ◄── Composition Root & Lifespan
└──────────┬───────────┘
           │
           ▼
┌──────────────────────┐
│  task_routes.py      │  ◄── Uses schemas.py (TaskResponse, TaskCreate)
└──────────┬───────────┘      FastAPI APIRouter for /tasks endpoints
           │
           ▼
┌──────────────────────┐
│   service.py (Svc)   │  ◄── Business logic & TaskNotFoundError / InvalidTaskError
└──────────┬───────────┘
           │
           ▼
┌──────────────────────┐
│   database.py (DB)   │  ◄── Uses TaskDTO & raw SQL queries
└──────────┬───────────┘      Seeds from sample_data.json if DB is empty
           │
           ▼
[      tasks.db      ]
```

### 📁 Project Directory Structure

```
BE-02-DB/
├── migrations/                                # Versioned SQL database migration scripts
│   ├── 001_create_tasks_table.sql            # Migration 001: Initial tasks table schema
│   └── 002_add_timestamps.sql                # Migration 002: Add created_at and updated_at columns
├── .gitignore                                 # Git ignore rules (excludes tasks.db, .venv/, __pycache__/)
├── requirements.txt                           # Python project dependencies (fastapi, uvicorn, pydantic)
├── sample_data.json                           # Initial JSON seed data for auto-populating tasks.db
├── database.py                                # DB Layer: TaskDTO, TaskRepository, migration runner, SQLite queries
├── service.py                                 # Service Layer: TaskService, TaskNotFoundError, InvalidTaskError
├── schemas.py                                 # API Layer: Pydantic schemas (TaskResponse, TaskCreate, TaskReplace, TaskUpdate, StatsResponse)
├── task_routes.py                             # API Layer Router: APIRouter handling /tasks endpoints
├── main.py                                    # Application Entry: Composition root, lifespan, / /health /stats routes
├── README.md                                  # Project documentation and architectural guide
├── W2 - Build your first CRUD API.pdf         # Assignment A1 specification PDF
└── W3 - Connecting your CRUD to the database.pdf # Assignment A2 specification PDF
```

### 📄 Detailed File Inventory & Responsibilities

| File / Directory | Layer / Purpose | Detailed Responsibilities |
|---|---|---|
| **`migrations/`** | Schema Migrations | Contains version-prefixed SQL migration files (`001_...sql`, `002_...sql`). |
| **`.gitignore`** | Version Control | Prevents generated files (`tasks.db`), virtual environment (`.venv/`), and compiled bytecode (`__pycache__/`) from being committed to Git. |
| **`requirements.txt`** | Dependencies | Specifies exact Python packages required (`fastapi`, `uvicorn[standard]`, `pydantic`). |
| **`sample_data.json`** | Seed Data | External JSON file pre-defining default task records (`title`, `done`). Loaded on first startup if `tasks.db` is empty. |
| **`database.py`** | Database / Persistence | Defines **`TaskDTO`** (`dataclass` with `created_at` & `updated_at`). **`TaskRepository`** includes `run_migrations()` to scan and execute pending `.sql` files, tracks versions in `schema_migrations`, manages raw SQL queries, and populates `GET /stats`. |
| **`service.py`** | Business / Service | Defines **`TaskService`** and domain exceptions (**`TaskNotFoundError`**, **`InvalidTaskError`**). Enforces business validation rules and separates **`replace_task`** (`PUT`) from **`patch_task`** (`PATCH`). |
| **`schemas.py`** | API Schemas | Defines Pydantic request/response models: **`TaskResponse`** (includes `created_at` & `updated_at`), **`TaskCreate`**, **`TaskReplace`**, **`TaskUpdate`**, and **`StatsResponse`**. |
| **`task_routes.py`** | API Router | Dedicated FastAPI `APIRouter(prefix="/tasks")`. Implements HTTP handlers for `GET /tasks` (with `?search` and `?done` filters), `GET /tasks/{id}`, `POST /tasks`, `PUT /tasks/{id}`, `PATCH /tasks/{id}`, and `DELETE /tasks/{id}`. |
| **`main.py`** | Application Entrypoint | Composition root. Configures FastAPI instance, mounts `task_router`, runs database lifespan migration runner & seeding (`init_db()`), and defines system endpoints (`GET /`, `GET /health`, `GET /stats`). |
| **`README.md`** | Documentation | Comprehensive developer documentation, setup instructions, architecture breakdown, DBeaver connection guide, migration guide, and progress checklist. |

---

## 🔄 Versioned Database Migrations System & Fresh DB Setup

Instead of destroying or manually editing the database when the schema changes, the project uses an automated, version-based SQL migration runner built into `database.py`:

### How Migrations Work:
1. **Tracking Table (`schema_migrations`)**:
   On application startup, SQLite creates a tracking table:
   ```sql
   CREATE TABLE IF NOT EXISTS schema_migrations (
       version INTEGER PRIMARY KEY,
       filename TEXT NOT NULL,
       applied_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
   );
   ```
2. **Sequential File Execution**:
   The runner scans `migrations/*.sql` sorted by filename (`001`, `002`, ...). Any migration version not present in `schema_migrations` is executed inside a SQL transaction and recorded.

3. **Fresh Database Replay & Seeding**:
   If `tasks.db` is deleted or created on a clean machine:
   - `run_migrations()` automatically executes `001_create_tasks_table.sql` and `002_add_timestamps.sql` in order.
   - `init_db()` detects `COUNT(*) == 0` and populates `sample_data.json` with initial timestamps.

### Applied Changesets & Timestamps:
- **`001_create_tasks_table.sql`**: Creates initial `tasks` table (`id`, `title`, `done`).
- **`002_add_timestamps.sql`**: Adds `created_at` and `updated_at` columns (`TIMESTAMP`).
- **Explicit Timestamp Handling**: To support SQLite `ALTER TABLE` rules cleanly across existing and new rows:
  - New insertions (`POST /tasks` & `sample_data.json` seeding) explicitly pass `created_at` and `updated_at` as `CURRENT_TIMESTAMP`.
  - Task updates (`PUT` & `PATCH`) automatically refresh `updated_at = CURRENT_TIMESTAMP`.

---

## 🚀 How to Install & Run

### 1. Prerequisites
- Python 3.10+ installed

### 2. Setup Virtual Environment & Install Dependencies
Navigate into the `BE-02-DB` directory:

```bash
cd BE-02-DB
python -m venv .venv
# On Windows (PowerShell / CMD):
.venv\Scripts\activate
# On macOS / Linux:
source .venv/bin/activate

pip install -r requirements.txt
```

### 3. Run the API Server
Start the development server with Uvicorn:

```bash
uvicorn main:app --reload
```

- Server runs at: `http://127.0.0.1:8000`
- Interactive Swagger UI documentation: `http://127.0.0.1:8000/docs`

---

## 🔌 Connecting to `tasks.db` with DBeaver

You can view, edit, and query the SQLite database using **DBeaver**:

1. Open **DBeaver**.
2. Click **Database** ➔ **New Database Connection** (or click the plug icon `+`).
3. Select **SQLite** from the driver list and click **Next**.
4. In the **Database file** path field, click **Browse...** and select the `tasks.db` file (located in the `BE-02-DB` directory).
5. Click **Test Connection** (if prompted, click *Download* to fetch the SQLite JDBC driver).
6. Click **Finish**.
7. Expand `tasks.db` ➔ `Tables` ➔ `tasks` to view the table schema and data rows in real-time!

---

## 📋 API Endpoints Table

| Method | Endpoint | Description | Success Status | Error Status |
|---|---|---|---|---|
| `GET` | `/` | API Root / Info | `200 OK` | - |
| `GET` | `/health` | Server Health & DB status check | `200 OK` | - |
| `GET` | `/stats` | Database Statistics (tables & row counts) | `200 OK` | - |
| `GET` | `/tasks` | List all tasks (Supports `?search=term` and `?done=true/false`) | `200 OK` | - |
| `GET` | `/tasks/{id}` | Get single task by ID | `200 OK` | `404 Not Found` |
| `POST` | `/tasks` | Create a new task (`title` required) | `201 Created` | `400 Bad Request` |
| `PUT` | `/tasks/{id}` | Full resource replacement (requires both `title` and `done`) | `200 OK` | `400 Bad Request` / `404` / `422` |
| `PATCH` | `/tasks/{id}` | Partial field update (`title` and/or `done` optional) | `200 OK` | `400 Bad Request` / `404 Not Found` |
| `DELETE` | `/tasks/{id}` | Delete task by ID | `204 No Content` | `404 Not Found` |

> 💡 **Strict REST Semantics (`PUT` vs `PATCH`)**:
> - **`PUT /tasks/{id}` (Full Replacement - RFC 9110)**: Uses the `TaskReplace` Pydantic model where **both `title` AND `done` are mandatory**. Omitting either field results in a `422 Unprocessable Entity` validation error.
> - **`PATCH /tasks/{id}` (Partial Update - RFC 5789)**: Uses the `TaskUpdate` Pydantic model where **all fields are optional (`title: Optional[str]`, `done: Optional[bool]`)**. Only fields explicitly sent by the client are modified in the database.
>
> | Endpoint | Schema Model | `{"title": "X", "done": true}` | `{"done": true}` (omitting title) |
> |---|---|---|---|
> | `PUT /tasks/{id}` | `TaskReplace` (Strict) | ✅ `200 OK` (Replaces resource) | ❌ `422 Unprocessable Entity` |
> | `PATCH /tasks/{id}` | `TaskUpdate` (Delta) | ✅ `200 OK` (Updates both) | ✅ `200 OK` (Updates `done` only) |

---

## 🛠️ Step-by-Step Progress & Stages

- [x] **Stage 0: Create SQLite database** – Auto-create `tasks.db`, define `tasks` table (`id`, `title`, `done`), and seed 3 default tasks if empty.
- [x] **Stage 1: Read endpoints** – Implement `GET /tasks` and `GET /tasks/{id}` using SQL queries and parameterized placeholders.
- [x] **Stage 2: Create endpoint** – Implement `POST /tasks` with validation (non-empty title) and SQL `INSERT`.
- [x] **Stage 3: Update & Delete endpoints** – Implement `PUT /tasks/{id}` and `DELETE /tasks/{id}` with correct status codes.
- [x] **Stage 4: Explore SQLite by hand** – Connect via DB Browser for SQLite or DBeaver and execute raw SQL queries.
- [x] **Stage 5: Documentation & Publishing** – Complete README, document example queries, and finalize repo setup.

---

## 🗄️ Sample SQL Queries (Stage 4 Exploration)

When inspecting `tasks.db` directly in DBeaver or DB Browser for SQLite:

```sql
-- List all tasks
SELECT * FROM tasks;

-- Filter completed tasks
SELECT * FROM tasks WHERE done = 1;

-- Count total tasks
SELECT COUNT(*) FROM tasks;

-- Mark a task as completed
UPDATE tasks SET done = 1 WHERE id = 1;

-- Delete completed tasks
DELETE FROM tasks WHERE done = 1;
```

### 📝 Stage 4 Direct DB Exploration Observation
> **Exploration Query**: `UPDATE tasks SET done = 1 WHERE id = 2;`
> **Result & Observation**: Executing this update directly inside DBeaver instantly modified the underlying `tasks.db` file. Calling `GET /tasks/2` via the FastAPI backend immediately returned `"done": true` without requiring an API server restart—confirming that the SQLite database file serves as the single source of truth for both DBeaver and the API.
