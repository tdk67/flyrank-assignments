# BE-01 Java 21 & Spring Boot 4.0 User Service

> **FlyRank Internship · Backend Track · Java 21 LTS & Virtual Threads**

A next-generation Spring Boot backend implementing the **BE-01 User Service** utilizing **Java 21 LTS** native platform features (**Virtual Threads / Project Loom**, **Record Patterns & Deconstruction**, **Pattern Matching for Switch**, and **Sequenced Collections**) on **Spring Boot 4.0.0-M1**.

---

## 🔍 Side-by-Side Code Comparison: Java 17 vs. Java 21

### 1. Record Pattern Deconstruction (JEP 440)

* **Java 17 Baseline (`java-17-springboot-3.5`)**:  
  Requires extracting record components via individual getter calls:
  ```java
  // UserServiceImpl.java (Java 17)
  @Override
  public UserResponse createUser(UserCreateRequest request) {
      UUID newId = UUID.randomUUID();
      NameDto name = request.name();
      String email = request.email();
      String telephone = request.telephone();
      
      UserResponse newRecord = new UserResponse(newId, name, email, telephone);
      return userRepository.save(newRecord);
  }
  ```

* **Java 21 Platform (`java-21-springboot-4.0`)**:  
  Deconstructs record patterns directly in pattern matching assertions:
  ```java
  // UserServiceImpl.java (Java 21)
  @Override
  public UserResponse createUser(UserCreateRequest request) {
      UUID newId = UUID.randomUUID();

      // Java 21 Record Pattern Deconstruction:
      if (request instanceof UserCreateRequest(NameDto name, String email, String telephone)) {
          UserResponse newRecord = new UserResponse(newId, name, email, telephone);
          return userRepository.save(newRecord);
      }
      ...
  }
  ```

---

### 2. Pattern Matching for `switch` with Guards (`when`) (JEP 441)

* **Java 17 Baseline (`java-17-springboot-3.5`)**:  
  Uses standard `if/else` checks:
  ```java
  // GlobalExceptionHandler.java (Java 17)
  String message = ex.getMessage();
  if (message != null && message.contains("Unrecognized field")) {
      return ResponseEntity.status(HttpStatus.UNPROCESSABLE_ENTITY)
              .body(new ErrorResponse("Unrecognized or forbidden field present in JSON payload"));
  }
  ```

* **Java 21 Platform (`java-21-springboot-4.0`)**:  
  Uses pattern matching `switch` expressions with null handling and boolean guard clauses (`when`):
  ```java
  // GlobalExceptionHandler.java (Java 21)
  String errorDetail = switch (message) {
      case String msg when msg.contains("Unrecognized field") ->
              "Unrecognized or forbidden field present in JSON payload";
      case String msg when msg.contains("JSON parse error") ->
              "Malformed JSON syntax payload";
      case null ->
              "Invalid JSON request body payload";
      default ->
              "Invalid JSON request body payload";
  };
  ```

---

### 3. Sequenced Collections Interface (JEP 431)

* **Java 17 Baseline (`java-17-springboot-3.5`)**:  
  Uses standard `List<UserResponse>` without unified encounter order methods:
  ```java
  // UserRepository.java (Java 17)
  public interface UserRepository {
      UserResponse save(UserResponse user);
      Optional<UserResponse> findById(UUID id);
  }
  ```

* **Java 21 Platform (`java-21-springboot-4.0`)**:  
  Uses `SequencedCollection<UserResponse>` for unified encounter order (`.getFirst()`, `.getLast()`, `.reversed()`):
  ```java
  // UserRepository.java (Java 21)
  public interface UserRepository {
      UserResponse save(UserResponse user);
      Optional<UserResponse> findById(UUID id);
      
      // Java 21 SequencedCollection interface:
      SequencedCollection<UserResponse> findAllSequenced();
  }
  ```

---

## ⚡ Runtime & Architectural Shifts: Spring Boot 3.4 vs. Spring Boot 4.0

| Feature / Architectural Aspect | Spring Boot 3.4.2 Baseline | Spring Boot 4.0.0-M1 Platform |
|---|---|---|
| **Minimum Java JDK** | **Java 17 LTS** | **Java 21 LTS** (Required baseline) |
| **Concurrency Model** | Heavy OS Platform Threads (1 MB stack per request worker) | **Virtual Threads** enabled natively (`spring.threads.virtual.enabled=true`) |
| **EE Specification** | Jakarta EE 10 (`jakarta.servlet` 6.0) | **Jakarta EE 11** (`jakarta.servlet` 6.1) |
| **HTTP Client** | `RestTemplate` / `WebClient` | Synchronous **`RestClient`** fluent API |
| **Null Safety** | Manual null checks | Native **JSpecify Annotations** (`@NullMarked`) |

---

## 🛠️ Build & Installation

```bash
cd Java-SpringBoot/BE-01-InMemory/java-21-springboot-4.0

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

Server runs on **Port 8002**:
* **Swagger UI:** `http://localhost:8002/docs` or `http://localhost:8002/swagger-ui.html`
* **OpenAPI Specs:** `http://localhost:8002/v3/api-docs`

---

## 🔌 API Endpoints & Curl Examples

```bash
# 1. Create a user
curl -i -X POST http://localhost:8002/user \
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
curl -i http://localhost:8002/user/a1b2c3d4-e5f6-7a8b-9c0d-1e2f3a4b5c6d
```
