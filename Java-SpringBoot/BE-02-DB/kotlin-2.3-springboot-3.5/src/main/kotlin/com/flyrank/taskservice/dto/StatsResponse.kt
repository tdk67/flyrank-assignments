package com.flyrank.taskservice.dto

import com.fasterxml.jackson.annotation.JsonProperty
import io.swagger.v3.oas.annotations.media.Schema

@Schema(description = "Database statistics payload")
data class StatsResponse(
    @field:Schema(description = "Database table names", example = "[\"TASKS\"]")
    val tables: List<String>,

    @field:Schema(description = "Total number of tasks", example = "5")
    @field:JsonProperty("total_tasks")
    val totalTasks: Long,

    @field:Schema(description = "Count of completed tasks", example = "2")
    @field:JsonProperty("done_tasks")
    val doneTasks: Long,

    @field:Schema(description = "Count of open tasks", example = "3")
    @field:JsonProperty("open_tasks")
    val openTasks: Long
)
