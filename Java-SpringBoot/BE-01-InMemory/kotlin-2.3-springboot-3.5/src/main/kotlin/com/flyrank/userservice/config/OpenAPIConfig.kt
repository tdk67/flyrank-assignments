package com.flyrank.userservice.config

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
                    .title("Flyrank BE-01 User Service (Kotlin 2.3 & K2 Compiler)")
                    .version("1.0.0")
                    .description("A Spring Boot 3.5 backend written in idiomatic Kotlin with K2 compiler, Data Classes, and Coroutines.")
            )
    }
}
