# PRD: BE-04-Containerize User Service

This Product Requirements Document (PRD) outlines the migration of the in-memory FastAPI User Service (`BE-01-FastAPI`) to a containerized application backed by a persistent database, with migrations managed via Liquibase.

---

## 1. Objectives

- **Persistence**: Migrate from the current volatile in-memory dictionary to a persistent relational database.
- **Containerization**: Package the FastAPI application, the database, and the migration runner using Docker and orchestrate them with Docker Compose.
- **Database Migrations**: Use **Liquibase** to manage database schema updates.
- **Health Monitoring**: Expose a `GET /health` endpoint that validates database connectivity.
- **Portability**: Ensure the entire system can be spun up locally (e.g., under WSL, macOS, or Linux) with a single command (`docker compose up`).
- **Robustness**: Maintain all strict validation constraints (like forbidding extra payload attributes) from `BE-01-FastAPI`.

---

## 2. Tech Stack & Architecture

We propose the following tech stack:

- **Web Framework**: FastAPI (retained from `BE-01`).
- **Database**: PostgreSQL.
- **Database Migration**: **Liquibase** (orchestrated as a Docker Compose service that runs before the FastAPI app starts).
- **ORM / Database Access**: SQLAlchemy or SQLModel (see comparison below).
- **Containerization**: Docker (FastAPI base image) and Docker Compose.
- **Configuration**: Pydantic Settings to manage credentials and connection strings via environment variables.

---

## 3. Detailed Comparison: SQLAlchemy vs SQLModel

To help you decide, here is a detailed breakdown of the two ORM approaches:

| Feature | SQLAlchemy 2.0 | SQLModel |
| :--- | :--- | :--- |
| **Concept** | Separation of concerns: Define SQL models (`models.py`) and Pydantic schemas (`schemas.py`) separately. | Unified models: A single class inherits from `SQLModel` and acts as both the database model and Pydantic schema. |
| **Pros** | - Industry standard, highly stable, and mature.<br>- Complete separation ensures that database changes don't automatically break API interfaces (safer for complex APIs). | - Eliminates duplicate code (no need to write separate request, response, and DB models).<br>- Very fast to write and maintain for simple schemas. |
| **Cons** | - Requires maintaining duplicate fields in both DB models and API schemas. | - Still in pre-1.0 development phase (versions `0.0.x`).<br>- Can run into version compatibility issues with major Pydantic or FastAPI upgrades. |
| **Recommendation**| **Recommended** for stability and strict validation control. | Excellent if you want the absolute absolute minimum lines of code. |

---

## 4. Liquibase Migration Strategy

We will configure Liquibase migrations using **Formatted SQL changelogs**. This keeps migrations simple to write and review.

### Liquibase Files:
1. `db/changelog/db.changelog-master.xml` – The master XML configuration that points to our migrations.
2. `db/changelog/changesets/001_create_users_table.sql` – The SQL-formatted changeset to create the users table.

### Docker Compose Orchestration:
```yaml
  db-migrate:
    image: liquibase/liquibase:latest
    volumes:
      - ./db:/liquibase/db
    command: >
      --changelog-file=db/changelog/db.changelog-master.xml
      --url=jdbc:postgresql://db:5432/user_db
      --username=postgres
      --password=postgrespassword
      update
    depends_on:
      db:
        condition: service_healthy
```
The FastAPI `web` container will wait for `db-migrate` to complete successfully (`service_completed_successfully`), ensuring tables always exist before the application serves requests.

---

## 5. Data Schema & Models

The database table `users` will map directly to the Pydantic schemas:

| Column Name  | Data Type | Constraints / Attributes |
| :---         | :---      | :--- |
| `id`         | UUID      | Primary Key, default auto-generated UUID |
| `first_name` | String    | Not Null, min length 1 |
| `last_name`  | String    | Not Null, min length 1 |
| `email`      | String    | Nullable, valid email |
| `telephone`  | String    | Nullable |

---

## 6. Verification & Testing Plan

1. **Docker Compose Launch**:
   ```bash
   docker compose up --build -d
   ```
2. **Endpoints Verification**:
   - Use `curl` to send `POST /user` and `GET /user/{id}` requests (confirming they behave identically to `BE-01`).
3. **Health Check Verification**:
   - Send `GET /health` and verify a `200 OK` response with DB status.
4. **Persistence Verification**:
   - Create a user, stop the containers (`docker compose down`), start them back up (`docker compose up -d`), and verify the user still exists via `GET /user/{id}`.
5. **Validation Verification**:
   - Attempt to send extra fields or malformed emails to verify the strict validation (e.g. `ConfigDict(extra="forbid")`) is still active and working.
