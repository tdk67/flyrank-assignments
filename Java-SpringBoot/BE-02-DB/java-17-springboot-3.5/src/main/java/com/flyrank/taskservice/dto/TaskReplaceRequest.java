package com.flyrank.taskservice.dto;

import io.swagger.v3.oas.annotations.media.Schema;
import jakarta.validation.constraints.NotBlank;
import jakarta.validation.constraints.NotNull;

/**
 * Task replacement payload accepted by PUT /tasks/{id} (both title & done are required).
 */
@Schema(description = "Payload accepted by PUT /tasks/{id} for full resource replacement")
public record TaskReplaceRequest(
        @Schema(description = "Full replacement title", example = "Updated Task Title", requiredMode = Schema.RequiredMode.REQUIRED)
        @NotBlank(message = "title is required and cannot be empty")
        String title,

        @Schema(description = "Full replacement completion status", example = "true", requiredMode = Schema.RequiredMode.REQUIRED)
        @NotNull(message = "done status is required for PUT full replacement")
        Boolean done
) {}
