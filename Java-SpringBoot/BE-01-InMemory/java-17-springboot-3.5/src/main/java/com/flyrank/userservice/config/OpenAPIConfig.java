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
                        .title("Flyrank BE-01 User Service (Java 17 & Spring Boot 3.5)")
                        .version("1.0.0")
                        .description("A Spring Boot backend that creates and retrieves users, "
                                + "keeping all data in memory. Java 17 re-implementation of Flyrank assignment BE-01."));
    }
}
