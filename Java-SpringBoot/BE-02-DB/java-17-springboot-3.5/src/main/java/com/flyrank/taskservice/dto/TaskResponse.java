package com.flyrank.taskservice.dto;

import com.fasterxml.jackson.annotation.JsonProperty;
import io.swagger.v3.oas.annotations.media.Schema;

/**
 * Task response representation matching FastAPI's TaskResponse model.
 */
@Schema(description = "Task resource response payload")
public record TaskResponse(
        @Schema(description = "Unique task identifier", example = "1")
        Long id,

        @Schema(description = "Task title / description", example = "Buy groceries")
        String title,

        @Schema(description = "Completion status", example = "false")
        boolean done,

        @Schema(description = "Creation timestamp", example = "2026-07-27T15:00:00")
        @JsonProperty("created_at")
        String createdAt,

        @Schema(description = "Last update timestamp", example = "2026-07-27T15:00:00")
        @JsonProperty("updated_at")
        String updatedAt
) {}
