package com.flyrank.taskservice.dto

import io.swagger.v3.oas.annotations.media.Schema

@Schema(description = "Payload accepted by PATCH /tasks/{id} for partial update")
data class TaskUpdateRequest(
    @field:Schema(description = "Updated task title (optional)", example = "Partially updated title")
    val title: String? = null,

    @field:Schema(description = "Updated completion status (optional)", example = "true")
    val done: Boolean? = null
)
