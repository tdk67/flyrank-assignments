# Java & Spring Boot Ecosystem Exploration

> **FlyRank Internship · Backend Multi-Flavor Exploration Track**

This repository explores modern Java & Kotlin backend development by building multi-flavor implementations of assignment projects (`BE-01-InMemory`, `BE-02-DB`, `BE-03-Auth`, `BE-04-Containerize`).

---

## 🏗️ Directory Hierarchy

```text
Java-SpringBoot/
├── BE-01-InMemory/
│   ├── java-17-springboot-3.5/      # Baseline Java 17 + Spring Boot 3.4.2 GA (Port 8001)
│   ├── java-21-springboot-4.0/      # Java 21 LTS + Spring Boot 4.0.0-M1 + Virtual Threads (Port 8002)
│   └── kotlin-2.3-springboot-3.5/    # Kotlin 2.3 + K2 Compiler + Spring Boot 3.4.2 GA (Port 8003)
│
├── BE-02-DB/
│   ├── java-17-springboot-3.5/      # Baseline Java 17 + Spring Data JPA + Persistent DB (Port 8011)
│   ├── java-21-springboot-4.0/      # Java 21 LTS + Spring Boot 4.0 + Virtual Threads + JPA (Port 8012)
│   └── kotlin-2.3-springboot-3.5/    # Kotlin 2.3 + Spring Data JPA + Persistent DB (Port 8013)
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
| **BE-02** | `java-17-springboot-3.5` | Java 17 | Spring Boot `3.4.2` GA | `8011` | H2 File / SQLite | Spring Data JPA, Entity Lifecycle, Database Seeding |
| **BE-02** | `java-21-springboot-4.0` | Java 21 | Spring Boot `4.0.0-M1` | `8012` | H2 File / SQLite | Virtual Threads, JPA, Record Patterns, Sequenced Collections |
| **BE-02** | `kotlin-2.3-springboot-3.5` | Kotlin 2.3 | Spring Boot `3.4.2` GA | `8013` | H2 File / SQLite | Spring Data JPA Kotlin, Null Safety, Automatic Seeding |
