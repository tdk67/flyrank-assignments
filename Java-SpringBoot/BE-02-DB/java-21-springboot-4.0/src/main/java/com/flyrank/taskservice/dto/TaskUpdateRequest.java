package com.flyrank.taskservice.dto;

import io.swagger.v3.oas.annotations.media.Schema;

@Schema(description = "Payload accepted by PATCH /tasks/{id} for partial update")
public record TaskUpdateRequest(
        @Schema(description = "Updated task title (optional)", example = "Partially updated title")
        String title,

        @Schema(description = "Updated completion status (optional)", example = "true")
        Boolean done
) {}
