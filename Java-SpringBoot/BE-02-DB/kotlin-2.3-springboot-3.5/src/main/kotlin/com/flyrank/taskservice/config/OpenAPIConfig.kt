package com.flyrank.taskservice.config

import io.swagger.v3.oas.models.OpenAPI
import io.swagger.v3.oas.models.info.Info
import org.springframework.context.annotation.Bean
import org.springframework.context.annotation.Configuration

@Configuration
class OpenAPIConfig {

    @Bean
    fun customOpenAPI(): OpenAPI {
        return OpenAPI()
            .info(
                Info()
                    .title("Flyrank BE-02 Task API (Kotlin 2.3 & Spring Data JPA)")
                    .version("1.0.0")
                    .description("Idiomatic Kotlin Task CRUD service with Spring Boot 3.4.2, Data Classes, and Spring Data JPA.")
            )
    }
}
