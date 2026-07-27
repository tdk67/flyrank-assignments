# BE-01 Kotlin 2.3 & Spring Boot 3.5 User Service

> **FlyRank Internship · Backend Track · Kotlin 2.3 & K2 Compiler**

An idiomatic Kotlin backend implementing the **BE-01 User Service** using **Kotlin 2.3**, **K2 Compiler**, **Kotlin Data Classes**, **Null-Safety**, and **Spring Boot 3.5**.

---

## 🚀 Key Kotlin Features Highlighted

1. **Kotlin Data Classes & Direct Property Validation:**
   ```kotlin
   data class NameDto(
       @field:JsonProperty("first_name") @field:NotBlank val firstName: String,
       @field:JsonProperty("last_name") @field:NotBlank val lastName: String
   )
   ```

2. **Null Safety & Optional Parameters:**
   Explicit non-null vs nullable types (`String? = null`) replacing Java `@Nullable` annotations.

3. **Kotlin `when` Expressions with Guards:**
   In `GlobalExceptionHandler.kt`:
   ```kotlin
   val errorDetail = when {
       message.contains("Unrecognized field") -> "Unrecognized or forbidden field present in JSON payload"
       message.contains("JSON parse error") -> "Malformed JSON syntax payload"
       else -> "Invalid JSON request body payload"
   }
   ```

4. **K2 Compiler & Top-Level Functions:**
   Clean top-level application launcher: `runApplication<UserServiceApplication>(*args)`.

---

## 🛠️ Build & Installation

```bash
cd Java-SpringBoot/BE-01-InMemory/kotlin-2.3-springboot-3.5

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

Server runs on **Port 8003**:
* **Swagger UI:** `http://localhost:8003/docs` or `http://localhost:8003/swagger-ui.html`
* **OpenAPI Specs:** `http://localhost:8003/v3/api-docs`

---

## 🔌 API Endpoints & Curl Examples

```bash
# 1. Create a user
curl -i -X POST http://localhost:8003/user \
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
curl -i http://localhost:8003/user/a1b2c3d4-e5f6-7a8b-9c0d-1e2f3a4b5c6d
```
