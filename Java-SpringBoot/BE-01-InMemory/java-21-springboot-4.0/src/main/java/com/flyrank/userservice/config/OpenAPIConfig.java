package com.flyrank.userservice.config;

import io.swagger.v3.oas.models.OpenAPI;
import io.swagger.v3.oas.models.info.Info;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;

/**
 * OpenAPI metadata configuration for Swagger UI docs.
 */
@Configuration
public class OpenAPIConfig {

    @Bean
    public OpenAPI customOpenAPI() {
        return new OpenAPI()
                .info(new Info()
                        .title("Flyrank BE-01 User Service (Java 21 LTS & Virtual Threads)")
                        .version("1.0.0")
                        .description("A Spring Boot 4.0 platform backend utilizing Virtual Threads (Project Loom), Record Patterns, and Sequenced Collections."));
    }
}
