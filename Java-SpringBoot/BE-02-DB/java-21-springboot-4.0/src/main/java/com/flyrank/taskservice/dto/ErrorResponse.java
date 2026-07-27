package com.flyrank.taskservice.dto;

import io.swagger.v3.oas.annotations.media.Schema;

@Schema(description = "Standard error response payload")
public record ErrorResponse(
        @Schema(description = "Readable error message detail", example = "Task with id '999' not found")
        String detail
) {}
