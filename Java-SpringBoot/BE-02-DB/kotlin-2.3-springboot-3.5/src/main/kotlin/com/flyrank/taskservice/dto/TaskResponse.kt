package com.flyrank.taskservice.dto

import com.fasterxml.jackson.annotation.JsonProperty
import io.swagger.v3.oas.annotations.media.Schema

@Schema(description = "Task resource response payload")
data class TaskResponse(
    @field:Schema(description = "Unique task identifier", example = "1")
    val id: Long,

    @field:Schema(description = "Task title / description", example = "Buy groceries")
    val title: String,

    @field:Schema(description = "Completion status", example = "false")
    val done: Boolean,

    @field:Schema(description = "Creation timestamp", example = "2026-07-27T15:00:00")
    @field:JsonProperty("created_at")
    val createdAt: String?,

    @field:Schema(description = "Last update timestamp", example = "2026-07-27T15:00:00")
    @field:JsonProperty("updated_at")
    val updatedAt: String?
)
