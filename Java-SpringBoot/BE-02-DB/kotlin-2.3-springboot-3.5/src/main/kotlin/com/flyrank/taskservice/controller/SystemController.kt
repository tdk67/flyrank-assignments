package com.flyrank.taskservice.controller

import com.flyrank.taskservice.dto.StatsResponse
import com.flyrank.taskservice.service.TaskService
import io.swagger.v3.oas.annotations.Operation
import io.swagger.v3.oas.annotations.tags.Tag
import org.springframework.web.bind.annotation.GetMapping
import org.springframework.web.bind.annotation.RestController

@RestController
@Tag(name = "system", description = "System, Health & Statistics Endpoints")
class SystemController(
    private val taskService: TaskService
) {

    @GetMapping("/")
    @Operation(summary = "Root API info")
    fun readRoot(): Map<String, Any> {
        return mapOf(
            "name" to "Task API with Database Persistence (Kotlin)",
            "version" to "1.0.0",
            "endpoints" to listOf("/tasks", "/tasks/{id}", "/stats")
        )
    }

    @GetMapping("/health")
    @Operation(summary = "System health check")
    fun healthCheck(): Map<String, String> {
        return mapOf("status" to "ok", "database" to "tasksdb")
    }

    @GetMapping("/stats")
    @Operation(summary = "Database statistics")
    fun getStats(): StatsResponse {
        return taskService.getStats()
    }
}
