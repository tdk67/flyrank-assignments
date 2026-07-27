# BE-02 Java 17 Task API with Database Persistence

> **FlyRank Internship · Backend Track · Java 17 Baseline with Database Persistence**

A Spring Boot CRUD service backed by persistent H2/SQLite database storage (`jdbc:h2:file:./data/tasksdb`) using **Flyway Versioned SQL Migrations**.

---

## 🚀 Features & Architecture

- **Flyway Database Migrations:** Migration scripts in `src/main/resources/db/migration/`:
  - `V1__create_tasks_table.sql`
  - `V2__add_timestamps.sql`
- **Auto-repair & Idempotent DDL:** `spring.flyway.repair-on-migrate=true` & `ADD COLUMN IF NOT EXISTS`.
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
- **OpenAPI Docs:** Interactive Swagger UI at `http://localhost:8011/docs`.

---

## 🛠️ Build & Installation

```bash
cd Java-SpringBoot/BE-02-DB/java-17-springboot-3.5

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

Server runs on **Port 8011**:
* **Swagger UI:** `http://localhost:8011/docs`
* **H2 Web Console:** `http://localhost:8011/h2-console` (JDBC URL: `jdbc:h2:file:./data/tasksdb`)

---

## 🔍 Troubleshooting

For Flyway migration checksum errors, duplicate column errors, or missing plugin dependency errors, refer to the master [BE-02-DB Troubleshooting Guide](../README.md#%EF%B8%8F-troubleshooting--gotchas-guide).
