package com.flyrank.taskservice.dto

import io.swagger.v3.oas.annotations.media.Schema

@Schema(description = "Standard error response payload")
data class ErrorResponse(
    @field:Schema(description = "Readable error message detail", example = "Task with id '999' not found")
    val detail: String
)
