# BE-02 Kotlin 2.3 Task API with Database Persistence

> **FlyRank Internship · Backend Track · Kotlin 2.3 & Spring Data JPA**

An idiomatic Kotlin Spring Boot CRUD service backed by persistent H2/SQLite database storage (`jdbc:h2:file:./data/tasksdb`) utilizing **Kotlin 2.3**, **K2 Compiler**, **Spring Data JPA**, **Kotlin Data Classes**, and **Flyway Versioned SQL Migrations**.

---

## 🚀 Features & Architecture

- **Flyway Database Migrations:** Migration scripts in `src/main/resources/db/migration/`:
  - `V1__create_tasks_table.sql`
  - `V2__add_timestamps.sql`
- **Idiomatic Kotlin:** Uses `data class`, non-null type safety, and extension functions.
- **Spring Data JPA & Entity Persistence:** Maps `TaskEntity` (`@Entity`) to persistent table `tasks`.
- **Database Seeding (`CommandLineRunner`):** Auto-seeds initial sample task data if the database file is empty on first startup.
- **Full CRUD Support:**
  - `GET /tasks` (with optional `?search` and `?done` filtering)
  - `GET /tasks/{id}`
  - `POST /tasks` (201 Created)
  - `PUT /tasks/{id}` (Full Replacement)
  - `PATCH /tasks/{id}` (Partial Update)
  - `DELETE /tasks/{id}` (204 No Content)
  - `GET /stats` (Database table & count breakdown)
  - `GET /health` & `GET /` (System endpoints)
- **OpenAPI Docs:** Interactive Swagger UI at `http://localhost:8013/docs`.

---

## 🛠️ Build & Installation

```bash
cd Java-SpringBoot/BE-02-DB/kotlin-2.3-springboot-3.5

# Generate Gradle Wrapper
gradle wrapper

# Run test suite
gradlew.bat test
```

---

## 🏃 Running the Application

```bash
gradlew.bat bootRun
```

Server runs on **Port 8013**:
* **Swagger UI:** `http://localhost:8013/docs`
* **H2 Web Console:** `http://localhost:8013/h2-console`

---

## 🔍 Troubleshooting

For Flyway migration checksum errors, duplicate column errors, or missing plugin dependency errors, refer to the master [BE-02-DB Troubleshooting Guide](../README.md#%EF%B8%8F-troubleshooting--gotchas-guide).
