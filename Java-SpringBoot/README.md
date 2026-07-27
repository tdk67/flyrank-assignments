# Java & Spring Boot Ecosystem Exploration: BE-01 User Service Flavors

> **FlyRank Internship · Multi-Flavor Backend Track**  
> A comparative study and implementation of the **BE-01 In-Memory User Service** across modern JVM languages, Spring Boot versions, and upcoming platform features.

---

## 🎯 Overview & Vision

The goal of this sub-project is to take the **BE-01 In-Memory User Service** (originally built with Python FastAPI) and recreate it across **3 distinct JVM flavors**. This hands-on comparison highlights:

1. How the **Java language** evolves from **Java 17 LTS to Java 21 LTS** (and beyond).
2. How **Spring Boot** transitions across major versions (**Spring Boot 3.x to Spring Boot 4.0**).
3. How **Kotlin 2.2+** with the **K2 Compiler** compares to modern Java in developer experience, concurrency, and syntax.

---

## 📁 Flavor Matrix & Subfolder Breakdown

```text
Java-SpringBoot/
├── BE-01-InMemory/               # BE-01 In-Memory User Service Implementations
│   ├── java-17-springboot-3.5/    # Stable Enterprise Baseline (Java 17 target + Spring Boot 3.5 + Gradlew)
│   ├── java-21-springboot-4.0/    # Next-Gen Platform (Java 21 native + Spring Boot 4.0 + Gradlew)
│   └── kotlin-2.3-springboot-3.5/  # Modern Idiomatic Kotlin (Kotlin 2.3 + K2 + Spring Boot 3.5 + Gradlew)
└── README.md                  # Master guide & technical comparison
```

### Flavor Details & Environment Setup

System Environment:
- **System JDK:** Java 21 LTS (`OpenLogic-OpenJDK 21.0.6`) at `C:\Data\Apps\openJDK21`
- **Gradle:** Gradle 9.4.1 at `C:\Data\Apps\gradle-9.4.1`

> 💡 **Targeting Java 17 on JDK 21:** You do not need to install a separate Java 17 JDK. Gradle toolchains and javac `--release 17` compile Java 17 compatible bytecode directly using your Java 21 JDK!

| Flavor | Language & Version | Framework Version | Port | Build Tool | Key Highlights |
|---|---|---|---|---|---|
| **[`java-17-springboot-3.5`](file:///c:/Data/work/genAI/FlyrankAI/Java-SpringBoot/BE-01-InMemory/java-17-springboot-3.5)** | Java 17 LTS (target) | Spring Boot `3.4.2` (GA) | `8001` | Gradle Wrapper (`gradlew`) | Enterprise Baseline, Java 17 Records, Jakarta Validation, Spring Web MVC |
| **[`java-21-springboot-4.0`](file:///c:/Data/work/genAI/FlyrankAI/Java-SpringBoot/BE-01-InMemory/java-21-springboot-4.0)** | Java 21 LTS (native) | Spring Boot `4.0.0-M1` (Milestone) | `8002` | Gradle Wrapper (`gradlew`) | Virtual Threads (Loom), Record Patterns, Switch Pattern Matching, Sequenced Collections |
| **[`kotlin-2.3-springboot-3.5`](file:///c:/Data/work/genAI/FlyrankAI/Java-SpringBoot/BE-01-InMemory/kotlin-2.3-springboot-3.5)** | Kotlin 2.3 | Spring Boot `3.4.2` (GA) | `8003` | Gradle Wrapper (`gradlew`) | K2 Compiler, Kotlin Data Classes, Coroutines, `when` Guards, Null Safety |

*Future Expansion Planned:* `java-21-quarkus`, `kotlin-2.2-micronaut`

---

## 💡 What's New: Java 17 → Java 21 LTS Migration Guide

Java 21 (released September 2023) is the most significant LTS release since Java 11. Key features include:

### 1. Virtual Threads (Project Loom — JEP 444)
* **What it solves:** Replaces expensive OS platform threads (1 MB stack per thread) with lightweight, managed JVM threads (few hundred bytes per thread). You can launch **millions** of concurrent threads.
* **In Spring Boot 3.2+ / 4.0:** Enable natively with a single configuration line:
  ```properties
  spring.threads.virtual.enabled=true
  ```
* **Impact:** Eliminates the need for complex reactive programming (RxJava / Project Reactor) for high-throughput I/O bound workloads.

### 2. Record Patterns & Deconstruction (JEP 440)
Deconstruct record values directly in `instanceof` checks or `switch` expressions:
```java
// Java 17: Record declaration
public record UserRecord(UUID id, String firstName, String lastName) {}

// Java 21: Deconstruction pattern matching
if (obj instanceof UserRecord(UUID id, String firstName, String lastName)) {
    System.out.println("User: " + firstName + " " + lastName + " (" + id + ")");
}
```

### 3. Pattern Matching for `switch` (JEP 441)
Exhaustive type checking, null handling, and guard clauses (`when`):
```java
String response = switch (result) {
    case UserRecord u when u.firstName().equals("Admin") -> "Admin access granted";
    case UserRecord u -> "Standard user: " + u.firstName();
    case ErrorRecord e -> "Error: " + e.message();
    case null -> "No result provided";
};
```

### 4. Sequenced Collections (JEP 431)
Fixes the historical lack of a unified interface for collections with a defined encounter order (`ArrayList`, `LinkedHashSet`, `ArrayDeque`):
```java
SequencedCollection<User> users = new ArrayList<>();
User first = users.getFirst();  // Unified API
User last  = users.getLast();
SequencedCollection<User> reversed = users.reversed();
```

### 5. Scoped Values & Structured Concurrency (Preview/Incubating — JEP 446 / 453)
* **Scoped Values:** A safer, immutable, and performant alternative to `ThreadLocal` when passing contextual data (e.g. SecurityContext) across virtual threads.
* **Structured Concurrency:** Treats groups of related tasks running in different threads as a single unit of work, simplifying error handling and cancellation.

---

## 🚀 Spring Boot Version Roadmap: 3.x vs. 4.0

### Spring Boot 3.x Generation (Current Active Baseline)
* Requires **Java 17** as the minimum version.
* Full migration to **Jakarta EE 10** (`jakarta.persistence.*`, `jakarta.validation.*`, `jakarta.servlet.*`).
* Introduces `RestClient` (synchronous HTTP client with fluent API) and native Observability via Micrometer.
* Native Virtual Thread support via `spring.threads.virtual.enabled=true`.

### Spring Boot 4.0 Generation (Upcoming Major Architecture)
* Powered by **Spring Framework 7**.
* **Java 21 LTS** is the absolute minimum required baseline.
* **Jakarta EE 11** baseline.
* Native Virtual Threads by default for Web MVC servlet containers (Tomcat / Jetty).
* Null-safety overhaul with JSpecify annotations (`@NullMarked`, `@Nullable`).
* First-class HTTP/3 and WebTransport protocol support.

---

## 🪶 Kotlin 2.3+ Highlights & Comparison with Java

Kotlin 2.0+ introduces the revolutionary **K2 Compiler**, dramatically improving frontend compilation speed, IDE responsiveness, and enabling advanced language features across 2.0–2.3+.

### Key Kotlin 2.0 / 2.1 / 2.2 / 2.3 Features

#### 1. Guards in `when` Expressions (Kotlin 2.1)
Adds boolean conditions directly inside type-matching `when` branches:
```kotlin
when (val response = userService.findUser(id)) {
    is UserResponse.Success if response.user.isActive -> processActiveUser(response.user)
    is UserResponse.Success -> processInactiveUser(response.user)
    is UserResponse.NotFound -> handleNotFound()
}
```

#### 2. Explicit Backing Fields (Kotlin 2.0 / 2.2)
Simplifies encapsulation of mutable state without creating a secondary `_property` variable:
```kotlin
class UserViewModel {
    // Explicit field keyword syntax
    val title: String
        field = "Initial Title"
        get() = field
}
```

#### 3. Context Parameters (Evolution of Context Receivers)
Pass implicit dependency contexts cleanly into functions without parameter pollution:
```kotlin
context(userContext: UserContext)
fun logUserAction(action: String) {
    println("User ${userContext.id} performed $action")
}
```

---

### Java vs. Kotlin Comparison Matrix

| Feature | Java 21 | Kotlin 2.2 |
|---|---|---|
| **Data Carriers** | `record User(UUID id, String name)` | `data class User(val id: UUID, val name: String)` |
| **Immutability** | Records are strictly immutable | Data classes support `val` (read-only) and `var` (mutable) |
| **Concurrency** | **Virtual Threads** (imperative thread-per-request) | **Coroutines** (cooperative async with `suspend`) |
| **Null Safety** | Checked manually or with JSpecify `@Nullable` | Built into the type system (`String` vs `String?`) |
| **Smart Casting** | `instanceof` with Pattern Matching | Automatic smart casting (enhanced by K2 compiler) |
| **Spring DSL** | `@RestController` annotations | Spring Kotlin Coroutines DSL / Router DSL |

---

## 📋 The BE-01 Implementation Spec Across All Flavors

Every flavor folder implements the **exact same specification** to allow direct comparison of code conciseness, performance, and structure.

### Endpoints

| Method | Endpoint | Status | Description |
|---|---|:---:|---|
| `POST` | `/user` | `201 Created` | Create user. Mandatory: `name` (`first_name` + `last_name`). Optional: `email`, `telephone`. Returns full user object. Rejects extra/malformed fields with `400`/`422`. |
| `GET` | `/user/{user_id}` | `200 OK` | Retrieve user by UUID. Returns `404 Not Found` if nonexistent. |
| `GET` | `/swagger-ui.html` | `200 OK` | Interactive OpenAPI documentation (Springdoc OpenAPI / Swagger UI). |

### Common In-Memory Storage Requirement
All implementations use a thread-safe, concurrent in-memory store:
```java
// Java: ConcurrentHashMap
private final Map<UUID, User> userStore = new ConcurrentHashMap<>();
```

---

## 🛣️ Next Steps & Roadmap

1. **Phase 1 (Baseline):** Implement `java-17-springboot-3.5` with Spring Web MVC, Jakarta Validation, and Springdoc.
2. **Phase 2 (Modern Java):** Implement `java-21-springboot-4.0` taking advantage of Virtual Threads, Records, and Record Patterns.
3. **Phase 3 (Kotlin):** Implement `kotlin-2.2-springboot-3.5` using Kotlin Data Classes, Coroutines, and K2 features.
4. **Phase 4 (Benchmark & Compare):** Measure memory footprint, startup time, throughput, and code lines across all 3 implementations.
