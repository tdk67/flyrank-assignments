package com.flyrank.taskservice.controller;

import com.flyrank.taskservice.dto.StatsResponse;
import com.flyrank.taskservice.service.TaskService;
import io.swagger.v3.oas.annotations.Operation;
import io.swagger.v3.oas.annotations.tags.Tag;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RestController;

import java.util.List;
import java.util.Map;

/**
 * System and Health check endpoints matching FastAPI main.py.
 */
@RestController
@Tag(name = "system", description = "System, Health & Statistics Endpoints")
public class SystemController {

    private final TaskService taskService;

    public SystemController(TaskService taskService) {
        this.taskService = taskService;
    }

    @GetMapping("/")
    @Operation(summary = "Root API info")
    public Map<String, Object> readRoot() {
        return Map.of(
                "name", "Task API with Database Persistence",
                "version", "1.0.0",
                "endpoints", List.of("/tasks", "/tasks/{id}", "/stats")
        );
    }

    @GetMapping("/health")
    @Operation(summary = "System health check")
    public Map<String, String> healthCheck() {
        return Map.of("status", "ok", "database", "tasksdb");
    }

    @GetMapping("/stats")
    @Operation(summary = "Database statistics")
    public StatsResponse getStats() {
        return taskService.getStats();
    }
}
