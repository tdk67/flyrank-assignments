package com.flyrank.taskservice.dto;

import io.swagger.v3.oas.annotations.media.Schema;
import jakarta.validation.constraints.NotBlank;

@Schema(description = "Payload accepted when creating a new task")
public record TaskCreateRequest(
        @Schema(description = "Task title (required, non-empty)", example = "Build Spring Boot CRUD API", requiredMode = Schema.RequiredMode.REQUIRED)
        @NotBlank(message = "title is required and cannot be empty")
        String title
) {}
