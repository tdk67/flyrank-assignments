package com.flyrank.userservice.dto;

import io.swagger.v3.oas.annotations.media.Schema;

/**
 * Standard error response payload matching FastAPI's {"detail": "..."} format.
 */
@Schema(description = "Standard error response payload")
public record ErrorResponse(
        @Schema(description = "Readable error message detail", example = "User with id '...' not found")
        String detail
) {}
