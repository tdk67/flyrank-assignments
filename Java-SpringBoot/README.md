# Java & Spring Boot Ecosystem Exploration

> **FlyRank Internship · Multi-Flavor Backend Track**  
> Comprehensive comparative exploration of Java 17 LTS, Java 21 LTS (with Virtual Threads), and Kotlin 2.3 across modern Spring Boot 3.4.2 GA and Spring Boot 4.0.0-M1 backend assignments.

---

## 📁 Repository Directory Hierarchy

```text
Java-SpringBoot/
├── BE-01-InMemory/
│   ├── java-17-springboot-3.5/      # Java 17 Baseline + Spring Boot 3.4.2 GA (Port 8001)
│   ├── java-21-springboot-4.0/      # Java 21 LTS + Spring Boot 4.0 + Virtual Threads (Port 8002)
│   └── kotlin-2.3-springboot-3.5/    # Kotlin 2.3 + Spring Boot 3.4.2 GA (Port 8003)
│
├── BE-02-DB/
│   ├── java-17-springboot-3.5/      # Java 17 + Spring Boot 3.4.2 + Spring Data JPA + Flyway (Port 8011)
│   ├── java-21-springboot-4.0/      # Java 21 LTS + Spring Boot 4.0 + Virtual Threads + JPA + Flyway (Port 8012)
│   └── kotlin-2.3-springboot-3.5/    # Kotlin 2.3 + Spring Data JPA + Flyway Migrations (Port 8013)
│
├── BE-03-Auth/
│   ├── java-17-springboot-3.5/      # Java 17 + Spring Security + Bearer JWT Auth (Port 8021)
│   ├── java-21-springboot-4.0/      # Java 21 LTS + Virtual Threads + Spring Security + JJWT (Port 8022)
│   └── kotlin-2.3-springboot-3.5/    # Kotlin 2.3 + Spring Security + Bearer JWT Auth (Port 8023)
│
└── README.md
```

---

## 📊 Complete Flavor Comparison Matrix

| Assignment | Flavor Subfolder | JDK / Language | Framework Version | Port | Storage / DB | Core Highlights |
|---|---|---|---|:---:|---|---|
| **BE-01** | `java-17-springboot-3.5` | Java 17 | Spring Boot `3.4.2` GA | `8001` | ConcurrentHashMap | Baseline Records, Spring MVC, Strict JSON validation |
| **BE-01** | `java-21-springboot-4.0` | Java 21 | Spring Boot `4.0.0-M1` | `8002` | ConcurrentHashMap | Virtual Threads, Record Pattern Deconstruction, Switch Guards |
| **BE-01** | `kotlin-2.3-springboot-3.5` | Kotlin 2.3 | Spring Boot `3.4.2` GA | `8003` | ConcurrentHashMap | K2 Compiler, Data Classes, `@get:JsonIgnore`, Coroutines |
| **BE-02** | `java-17-springboot-3.5` | Java 17 | Spring Boot `3.4.2` GA | `8011` | H2 File / SQLite | Spring Data JPA, Entity Lifecycle, Flyway SQL Migrations |
| **BE-02** | `java-21-springboot-4.0` | Java 21 | Spring Boot `4.0.0-M1` | `8012` | H2 File / SQLite | Virtual Threads, JPA, Record Patterns, Flyway SQL Migrations |
| **BE-02** | `kotlin-2.3-springboot-3.5` | Kotlin 2.3 | Spring Boot `3.4.2` GA | `8013` | H2 File / SQLite | Spring Data JPA Kotlin, Null Safety, Flyway SQL Migrations |
| **BE-03** | `java-17-springboot-3.5` | Java 17 | Spring Boot `3.4.2` GA | `8021` | In-Memory / BCrypt | Spring Security 6.x, Bearer JWT Auth, JJWT 0.12.6 |
| **BE-03** | `java-21-springboot-4.0` | Java 21 | Spring Boot `4.0.0-M1` | `8022` | In-Memory / BCrypt | Virtual Threads, Spring Security, Record Patterns, JJWT |
| **BE-03** | `kotlin-2.3-springboot-3.5` | Kotlin 2.3 | Spring Boot `3.4.2` GA | `8023` | In-Memory / BCrypt | Kotlin Spring Security DSL, Data Classes, Bearer JWT Auth |
