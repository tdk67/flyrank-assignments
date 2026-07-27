# Java & Spring Boot Ecosystem Exploration: BE-02 Task API with Database Persistence

> **FlyRank Internship · Multi-Flavor Backend Track**  
> Implementation of the **BE-02 Task API** with disk-backed database persistence (SQLite / H2 File-backed database), Spring Data JPA, Flyway versioned SQL database migrations, and CRUD operations across 3 JVM flavors.

---

## 📁 Flavor Matrix & Subfolder Breakdown

```text
Java-SpringBoot/BE-02-DB/
├── java-17-springboot-3.5/      # Baseline (Java 17 + Spring Boot 3.4.2 GA + Spring Data JPA + Flyway)
├── java-21-springboot-4.0/      # Next-Gen Platform (Java 21 + Spring Boot 4.0.0-M1 + Virtual Threads + JPA)
├── kotlin-2.3-springboot-3.5/    # Idiomatic Kotlin (Kotlin 2.3 + Spring Boot 3.4.2 GA + Spring Data JPA)
└── README.md                    # Master guide & technical specification
```

### Flavor Overview

| Flavor | Language & Version | Framework Version | Port | Database | Build Tool | Migration Engine | Key Features |
|---|---|---|:---:|---|---|---|---|
| **`java-17-springboot-3.5`** | Java 17 LTS (target) | Spring Boot `3.4.2` GA | `8011` | H2 File / SQLite | Gradlew | Flyway | Java 17 Records, Spring Data JPA, Jakarta Validation |
| **`java-21-springboot-4.0`** | Java 21 LTS (native) | Spring Boot `4.0.0-M1` | `8012` | H2 File / SQLite | Gradlew | Flyway | Virtual Threads, JPA, Record Patterns, Sequenced Collections |
| **`kotlin-2.3-springboot-3.5`** | Kotlin 2.3 | Spring Boot `3.4.2` GA | `8013` | H2 File / SQLite | Gradlew | Flyway | K2 Compiler, Spring Data JPA Kotlin, Data Classes |

---

## 🛠️ Troubleshooting & Gotchas Guide

### 1. Flyway Dependency Resolution Error (`Could not find org.flywaydb:flyway-database-h2:.`)

* **Symptom / Error Log:**
  ```text
  > Task :compileJava FAILED
  Could not resolve all files for configuration ':compileClasspath'.
     > Could not find org.flywaydb:flyway-database-h2:.
  ```
* **What Happened:**
  Declaring `implementation("org.flywaydb:flyway-database-h2")` without a version in Gradle when Spring Boot's BOM does not manage `flyway-database-h2` causes Gradle to evaluate the artifact string as `:flyway-database-h2:`. In Flyway 10, H2 database support is built directly inside `flyway-core`.
* **How to Fix:**
  Omit `flyway-database-h2` and use standard `flyway-core`:
  ```kotlin
  dependencies {
      implementation("org.flywaydb:flyway-core")
  }
  ```

---

### 2. Flyway Migration Checksum Mismatch (`Validate failed: Migrations have failed validation`)

* **Symptom / Error Log:**
  ```text
  org.flywaydb.core.api.exception.FlywayValidateException: Validate failed: Migrations have failed validation
  Detected failed migration to version 2 (add timestamps).
  Please remove any half-completed changes then run repair to fix the schema history.
  ```
* **What Happened:**
  During local development, a SQL migration script (`V2__add_timestamps.sql`) was edited or updated *after* Flyway had already executed it and recorded its checksum in the `flyway_schema_history` table inside `./data/tasksdb`. On application startup, Flyway detected that the script's checksum on disk differed from the recorded checksum.
* **How to Fix:**
  1. Add `spring.flyway.repair-on-migrate=true` to `application.properties`:
     ```properties
     spring.flyway.repair-on-migrate=true
     ```
     This instructs Flyway to automatically repair checksum mismatches and failed migration entries in `flyway_schema_history` on startup.
  2. Alternatively, delete the local `./data/` folder to start with a fresh database.

---

### 3. Duplicate Column Error (`JdbcSQLSyntaxErrorException: Duplicate column name "CREATED_AT"`)

* **Symptom / Error Log:**
  ```text
  Caused by: org.h2.jdbc.JdbcSQLSyntaxErrorException: Duplicate column name "CREATED_AT"; SQL statement:
  -- Migration V2: Add created_at and updated_at timestamp columns to tasks table
  ALTER TABLE tasks ADD COLUMN created_at...
  ```
* **What Happened:**
  A migration script failed halfway through execution or was re-run against an existing database file `./data/tasksdb` where the column `CREATED_AT` had already been added by a previous partial run. Because the DDL lacked an `IF NOT EXISTS` check, H2 rejected adding an existing column.
* **How to Fix:**
  Use idempotent DDL statements in Flyway SQL scripts:
  ```sql
  -- Migration V2: Add created_at and updated_at timestamp columns to tasks table
  ALTER TABLE tasks ADD COLUMN IF NOT EXISTS created_at VARCHAR(64) DEFAULT CURRENT_TIMESTAMP NOT NULL;
  ALTER TABLE tasks ADD COLUMN IF NOT EXISTS updated_at VARCHAR(64) DEFAULT CURRENT_TIMESTAMP NOT NULL;
  ```

---

### 4. Hibernate Schema Validation Failure (`SchemaManagementException: Schema-validation: missing column`)

* **Symptom / Error Log:**
  ```text
  Caused by: org.hibernate.tool.schema.spi.SchemaManagementException: Schema-validation: missing column [created_at] in table [tasks]
  ```
* **What Happened:**
  Hibernate `spring.jpa.hibernate.ddl-auto=validate` strictly checks that every `@Column(nullable = false)` in JPA entities matches the database column nullability and existence created by Flyway. If Flyway creates columns without `NOT NULL` constraints or before Hibernate initializes, schema validation fails.
* **How to Fix:**
  Ensure Flyway DDL matches JPA entity column definitions (including `NOT NULL` and `DEFAULT` constraints) and set `spring.jpa.hibernate.ddl-auto=validate` (or `update`).
