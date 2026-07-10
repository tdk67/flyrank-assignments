# BE-01 FastAPI User Service

*Flyrank assignment BE-01*

A small, minimalistic FastAPI backend with two endpoints for creating and
retrieving users. All data is kept **in memory** (no database) — restarting
the server clears all users.

## What it does

- `POST /user` — create a user.
  - Accepts JSON with a mandatory `name` (`first_name` + `last_name`) and
    optional `email` and `telephone`.
  - Generates a unique `id` (UUID) for the user and returns the full user
    record with HTTP `201 Created`.
  - Rejects malformed input (missing mandatory fields, wrong types, invalid
    email format, unrecognized/unspecified fields) with a readable JSON
    error message and HTTP `422 Unprocessable Entity`.
- `GET /user/{user_id}` — retrieve a user.
  - Returns the user record as JSON with HTTP `200 OK` if `user_id` exists.
  - Returns HTTP `404 Not Found` with a JSON error message if it doesn't.

Interactive OpenAPI (Swagger) documentation is generated automatically by
FastAPI from the code's type annotations and docstrings — no extra setup
required.

## Requirements

- Python **3.12.x**

## Installation

```bash
# 1. Clone / open the project directory
cd BE-01-FastAPI

# 2. Create and activate a virtual environment
python -m venv .venv

# Windows
.venv\Scripts\activate

# macOS / Linux
source .venv/bin/activate

# 3. Install dependencies
pip install -r requirements.txt
```

## Running the app

```bash
uvicorn main:app --reload
```

The API is now available at `http://127.0.0.1:8000`.

## API documentation

Once the server is running, open:

- Swagger UI: http://127.0.0.1:8000/docs
- ReDoc: http://127.0.0.1:8000/redoc
- Raw OpenAPI schema: http://127.0.0.1:8000/openapi.json

## Testing the endpoints with curl

### Create a user (all fields)

```bash
curl -i -X POST http://127.0.0.1:8000/user \
  -H "Content-Type: application/json" \
  -d '{"name":{"first_name":"Jane","last_name":"Doe"},"email":"jane.doe@example.com","telephone":"+1-555-0100"}'
```

Expected: `201 Created` with the user record, including the generated `id`.

### Create a user (only the mandatory name)

```bash
curl -i -X POST http://127.0.0.1:8000/user \
  -H "Content-Type: application/json" \
  -d '{"name":{"first_name":"John","last_name":"Smith"}}'
```

Expected: `201 Created`, with `email` and `telephone` returned as `null`.

### Create a user — missing mandatory field (error case)

```bash
curl -i -X POST http://127.0.0.1:8000/user \
  -H "Content-Type: application/json" \
  -d '{"email":"a@b.com"}'
```

Expected: `422 Unprocessable Entity` with a readable error message, e.g.
`{"detail":"name: Field required"}`.

### Create a user — unspecified/extra field (error case)

```bash
curl -i -X POST http://127.0.0.1:8000/user \
  -H "Content-Type: application/json" \
  -d '{"name":{"first_name":"Jane","last_name":"Doe"},"age":30}'
```

Expected: `422 Unprocessable Entity`, e.g.
`{"detail":"age: Extra inputs are not permitted"}` — unspecified parameters
are rejected rather than silently ignored.

### Get an existing user

Replace `{user_id}` with an id returned by one of the `POST` calls above.

```bash
curl -i http://127.0.0.1:8000/user/{user_id}
```

Expected: `200 OK` with the user record as JSON.

### Get a non-existing user (error case)

```bash
curl -i http://127.0.0.1:8000/user/00000000-0000-0000-0000-000000000000
```

Expected: `404 Not Found`, e.g.
`{"detail":"User with id '00000000-0000-0000-0000-000000000000' not found"}`.

## Project structure

```
BE-01-FastAPI/
├── main.py            # FastAPI app: models, in-memory store, routes
├── requirements.txt    # Python dependencies
├── .gitignore
└── README.md
```
