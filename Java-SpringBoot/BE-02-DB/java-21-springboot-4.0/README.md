# BE-02 Java 21 Task API with Database Persistence

> **FlyRank Internship · Backend Track · Java 21 LTS, Spring Boot 4.0 & Virtual Threads**

A Spring Boot CRUD service backed by persistent H2/SQLite database storage (`jdbc:h2:file:./data/tasksdb`) utilizing **Java 21 LTS**, **Virtual Threads (Project Loom)**, **Record Pattern Deconstruction**, **Sequenced Collections**, and **Flyway Versioned SQL Migrations**.

---

## 🚀 Features & Architecture

- **Flyway Database Migrations:** Migration scripts in `src/main/resources/db/migration/`:
  - `V1__create_tasks_table.sql`
  - `V2__add_timestamps.sql`
- **Virtual Threads Enabled:** `spring.threads.virtual.enabled=true` in `application.properties`.
- **Spring Data JPA & Entity Persistence:** Maps `TaskEntity` (`@Entity`) to persistent table `tasks`.
- **Java 21 Record Pattern Deconstruction:** Unpacks records in pattern matching (`request instanceof TaskCreateRequest(String title)`).
- **Sequenced Collections:** `SequencedCollection<TaskEntity>` used in `TaskRepository.java`.
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
- **OpenAPI Docs:** Interactive Swagger UI at `http://localhost:8012/docs`.

---

## 🛠️ Build & Installation

```bash
cd Java-SpringBoot/BE-02-DB/java-21-springboot-4.0

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

Server runs on **Port 8012**:
* **Swagger UI:** `http://localhost:8012/docs`
* **H2 Web Console:** `http://localhost:8012/h2-console`

---

## 🔍 Troubleshooting

For Flyway migration checksum errors, duplicate column errors, or missing plugin dependency errors, refer to the master [BE-02-DB Troubleshooting Guide](../README.md#%EF%B8%8F-troubleshooting--gotchas-guide).
