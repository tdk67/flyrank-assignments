package com.flyrank.taskservice.config;

import io.swagger.v3.oas.models.OpenAPI;
import io.swagger.v3.oas.models.info.Info;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;

@Configuration
public class OpenAPIConfig {

    @Bean
    public OpenAPI customOpenAPI() {
        return new OpenAPI()
                .info(new Info()
                        .title("Flyrank BE-02 Task API (Java 17 & Spring Data JPA)")
                        .version("1.0.0")
                        .description("Task CRUD service backed by persistent H2/SQLite database with search, filtering, and stats."));
    }
}
