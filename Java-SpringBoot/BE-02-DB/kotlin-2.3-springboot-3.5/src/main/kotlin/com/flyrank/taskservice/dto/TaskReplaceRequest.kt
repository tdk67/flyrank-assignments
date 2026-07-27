package com.flyrank.taskservice.dto

import io.swagger.v3.oas.annotations.media.Schema
import jakarta.validation.constraints.NotBlank
import jakarta.validation.constraints.NotNull

@Schema(description = "Payload accepted by PUT /tasks/{id} for full resource replacement")
data class TaskReplaceRequest(
    @field:Schema(description = "Full replacement title", example = "Updated Task Title", requiredMode = Schema.RequiredMode.REQUIRED)
    @field:NotBlank(message = "title is required and cannot be empty")
    val title: String? = null,

    @field:Schema(description = "Full replacement completion status", example = "true", requiredMode = Schema.RequiredMode.REQUIRED)
    @field:NotNull(message = "done status is required for PUT full replacement")
    val done: Boolean? = null
)
