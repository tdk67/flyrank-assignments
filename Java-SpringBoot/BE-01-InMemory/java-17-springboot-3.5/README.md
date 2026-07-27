# BE-01 Java 17 & Spring Boot 3.5 User Service

> **FlyRank Internship · Backend Track · Java 17 Baseline**

A clean, production-grade Spring Boot backend that implements the **BE-01 In-Memory User Service** spec using **Java 17 LTS** and **Spring Boot 3.5** (Spring Boot 3.4+ generation). All data is stored in a thread-safe in-memory repository (`ConcurrentHashMap`).

---

## 🚀 Features & Architecture

- **Java 17 Records:** Used for immutable Data Transfer Objects (`NameDto`, `UserCreateRequest`, `UserResponse`, `ErrorResponse`) with zero boilerplate.
- **Jakarta Bean Validation:** Declarative request validation (`@NotBlank`, `@Email`, `@Valid`, `@NotNull`).
- **Strict JSON Parsing:** Replicates Pydantic's `extra="forbid"` rule (`spring.jackson.deserialization.fail-on-unknown-properties=true`), rejecting unknown JSON attributes with `422 Unprocessable Entity`.
- **Clean Architecture & Separation of Concerns:**
  - `controller`: REST API endpoints & HTTP mapping
  - `service`: Business logic & UUID generation
  - `repository`: Thread-safe data storage abstraction
  - `exception`: Global Exception Handler mapping exceptions to `404 Not Found` and `422 Unprocessable Entity` JSON responses
  - `config`: OpenAPI documentation configuration
- **OpenAPI & Swagger UI:** Automated documentation via Springdoc OpenAPI (`http://localhost:8000/swagger-ui.html`).

---

## 🛠️ Requirements

- **JDK:** Java 17+ (e.g. OpenLogic-OpenJDK 21 LTS installed on system)
- **Build Tool:** Gradle 8.x / 9.x (or system Gradle at `C:\Data\Apps\gradle-9.4.1`)

---

## 📦 Build & Installation

```bash
# Navigate to the project directory
cd Java-SpringBoot/java-17-springboot-3.5

# Build the application
gradle build

# Run unit and integration tests
gradle test
```

---

## 🏃 Running the Application

```bash
gradle bootRun
```

The server starts at `http://localhost:8000`.

* **Swagger UI:** `http://localhost:8000/swagger-ui.html`
* **OpenAPI Specs (JSON):** `http://localhost:8000/v3/api-docs`

---

## 🔌 API Endpoints & Curl Examples

| Method | Route | Status Code | Description |
|---|---|:---:|---|
| `POST` | `/user` | `201 Created` | Create user (`first_name`, `last_name` mandatory, `email`/`telephone` optional). Rejects unknown fields with `422`. |
| `GET` | `/user/{user_id}` | `200 OK` | Retrieve user by UUID. Returns `404 Not Found` if missing. |

### Curl Usage Examples

```bash
# 1. Create a user
curl -i -X POST http://localhost:8000/user \
  -H "Content-Type: application/json" \
  -d '{
    "name": {
      "first_name": "Jane",
      "last_name": "Doe"
    },
    "email": "jane.doe@example.com",
    "telephone": "+1-555-0199"
  }'

# 2. Retrieve user by ID
curl -i http://localhost:8000/user/a1b2c3d4-e5f6-7a8b-9c0d-1e2f3a4b5c6d

# 3. Test validation error (missing first_name -> 422)
curl -i -X POST http://localhost:8000/user \
  -H "Content-Type: application/json" \
  -d '{"name": {"last_name": "Doe"}}'

# 4. Test extra forbidden field rejection (extra field -> 422)
curl -i -X POST http://localhost:8000/user \
  -H "Content-Type: application/json" \
  -d '{
    "name": {"first_name": "Jane", "last_name": "Doe"},
    "extra_field": "disallowed"
  }'
```

---

## 💡 Python FastAPI vs Java 17 Comparison

| Feature | Python FastAPI | Java 17 + Spring Boot 3.5 |
|---|---|---|
| **Data Models** | Pydantic `BaseModel` | Java 17 `record` |
| **Field Validation** | `Field(..., min_length=1)` | `@NotBlank`, `@Email`, `@Valid` |
| **Extra Fields** | `ConfigDict(extra="forbid")` | `spring.jackson.deserialization.fail-on-unknown-properties=true` |
| **In-Memory Store** | Python `dict[UUID, UserRecord]` | Java `ConcurrentHashMap<UUID, UserResponse>` |
| **Error Handling** | `@app.exception_handler` | `@RestControllerAdvice` + `@ExceptionHandler` |
| **API Docs** | Swagger UI built-in (`/docs`) | Springdoc OpenAPI (`/swagger-ui.html`) |
