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

### Module Responsibilities:

| File | Layer | Description |
|---|---|---|
| `sample_data.json` | Seed Data | External JSON file pre-defining default tasks (`title`, `done`). |
| `database.py` | DB / Persistence | Defines `TaskDTO` and `TaskRepository`. Manages SQLite connections, table creation, JSON seeding, and raw SQL queries (`SELECT`, `INSERT`, etc.). |
| `service.py` | Business / Service | Defines `TaskService` and domain exceptions (`TaskNotFoundError`, `InvalidTaskError`). Handles domain logic and coordinates with `TaskRepository`. |
| `schemas.py` | API Models | Pydantic models (`TaskResponse`, `TaskCreate`, `TaskUpdate`) used for API request parsing and response formatting. |
| `task_routes.py` | API Router | Dedicated FastAPI `APIRouter` for `/tasks` endpoints. Converts service domain errors to HTTP status codes (`400`, `404`). |
| `main.py` | Application Entry | Composition root. Configures FastAPI app, mounts `task_router`, handles database lifespan startup, and defines root/health endpoints. |

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
| `GET` | `/tasks` | List all tasks | `200 OK` | - |
| `GET` | `/tasks/{id}` | Get single task by ID | `200 OK` | `404 Not Found` |
| `POST` | `/tasks` | Create a new task (`title` required) | `201 Created` | `400 Bad Request` |
| `PUT` | `/tasks/{id}` | Update task `title` and/or `done` status | `200 OK` | `400 Bad Request` / `404 Not Found` |
| `DELETE` | `/tasks/{id}` | Delete task by ID | `204 No Content` | `404 Not Found` |

---

## 🛠️ Step-by-Step Progress & Stages

- [x] **Stage 0: Create SQLite database** – Auto-create `tasks.db`, define `tasks` table (`id`, `title`, `done`), and seed 3 default tasks if empty.
- [x] **Stage 1: Read endpoints** – Implement `GET /tasks` and `GET /tasks/{id}` using SQL queries and parameterized placeholders.
- [x] **Stage 2: Create endpoint** – Implement `POST /tasks` with validation (non-empty title) and SQL `INSERT`.
- [ ] **Stage 3: Update & Delete endpoints** – Implement `PUT /tasks/{id}` and `DELETE /tasks/{id}` with correct status codes.
- [ ] **Stage 4: Explore SQLite by hand** – Connect via DB Browser for SQLite or DBeaver and execute raw SQL queries.
- [ ] **Stage 5: Documentation & Publishing** – Complete README, document example queries, and finalize repo setup.

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
