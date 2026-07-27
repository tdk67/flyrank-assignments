package com.flyrank.taskservice.controller;

import com.flyrank.taskservice.dto.*;
import com.flyrank.taskservice.service.TaskService;
import io.swagger.v3.oas.annotations.Operation;
import io.swagger.v3.oas.annotations.tags.Tag;
import jakarta.validation.Valid;
import org.springframework.http.HttpStatus;
import org.springframework.http.MediaType;
import org.springframework.web.bind.annotation.*;

import java.util.List;

/**
 * REST Controller exposing Task CRUD API endpoints.
 */
@RestController
@RequestMapping("/tasks")
@Tag(name = "tasks", description = "Task Management CRUD Endpoints")
public class TaskController {

    private final TaskService taskService;

    public TaskController(TaskService taskService) {
        this.taskService = taskService;
    }

    @GetMapping(produces = MediaType.APPLICATION_JSON_VALUE)
    @Operation(summary = "List all tasks with optional search/filtering")
    public List<TaskResponse> getTasks(
            @RequestParam(name = "search", required = false) String search,
            @RequestParam(name = "done", required = false) Boolean done
    ) {
        return taskService.getAllTasks(search, done);
    }

    @GetMapping(value = "/{task_id}", produces = MediaType.APPLICATION_JSON_VALUE)
    @Operation(summary = "Get task by ID")
    public TaskResponse getTask(@PathVariable("task_id") Long taskId) {
        return taskService.getTaskById(taskId);
    }

    @PostMapping(consumes = MediaType.APPLICATION_JSON_VALUE, produces = MediaType.APPLICATION_JSON_VALUE)
    @ResponseStatus(HttpStatus.CREATED)
    @Operation(summary = "Create a new task")
    public TaskResponse createTask(@Valid @RequestBody TaskCreateRequest request) {
        return taskService.createTask(request);
    }

    @PutMapping(value = "/{task_id}", consumes = MediaType.APPLICATION_JSON_VALUE, produces = MediaType.APPLICATION_JSON_VALUE)
    @Operation(summary = "Replace task by ID (Full Replacement)")
    public TaskResponse updateTask(
            @PathVariable("task_id") Long taskId,
            @Valid @RequestBody TaskReplaceRequest request
    ) {
        return taskService.replaceTask(taskId, request);
    }

    @PatchMapping(value = "/{task_id}", consumes = MediaType.APPLICATION_JSON_VALUE, produces = MediaType.APPLICATION_JSON_VALUE)
    @Operation(summary = "Partially update task by ID")
    public TaskResponse patchTask(
            @PathVariable("task_id") Long taskId,
            @RequestBody TaskUpdateRequest request
    ) {
        return taskService.patchTask(taskId, request);
    }

    @DeleteMapping("/{task_id}")
    @ResponseStatus(HttpStatus.NO_CONTENT)
    @Operation(summary = "Delete task by ID")
    public void deleteTask(@PathVariable("task_id") Long taskId) {
        taskService.deleteTask(taskId);
    }
}
