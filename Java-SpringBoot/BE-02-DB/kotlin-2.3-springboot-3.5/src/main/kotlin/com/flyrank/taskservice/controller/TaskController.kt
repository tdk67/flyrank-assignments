package com.flyrank.taskservice.controller

import com.flyrank.taskservice.dto.*
import com.flyrank.taskservice.service.TaskService
import io.swagger.v3.oas.annotations.Operation
import io.swagger.v3.oas.annotations.tags.Tag
import jakarta.validation.Valid
import org.springframework.http.HttpStatus
import org.springframework.http.MediaType
import org.springframework.web.bind.annotation.*

@RestController
@RequestMapping("/tasks")
@Tag(name = "tasks", description = "Task Management CRUD Endpoints (Kotlin 2.3 & K2 Compiler)")
class TaskController(
    private val taskService: TaskService
) {

    @GetMapping(produces = [MediaType.APPLICATION_JSON_VALUE])
    @Operation(summary = "List all tasks with optional search/filtering")
    fun getTasks(
        @RequestParam(name = "search", required = false) search: String?,
        @RequestParam(name = "done", required = false) done: Boolean?
    ): List<TaskResponse> {
        return taskService.getAllTasks(search, done)
    }

    @GetMapping(value = ["/{task_id}"], produces = [MediaType.APPLICATION_JSON_VALUE])
    @Operation(summary = "Get task by ID")
    fun getTask(@PathVariable("task_id") taskId: Long): TaskResponse {
        return taskService.getTaskById(taskId)
    }

    @PostMapping(consumes = [MediaType.APPLICATION_JSON_VALUE], produces = [MediaType.APPLICATION_JSON_VALUE])
    @ResponseStatus(HttpStatus.CREATED)
    @Operation(summary = "Create a new task")
    fun createTask(@Valid @RequestBody request: TaskCreateRequest): TaskResponse {
        return taskService.createTask(request)
    }

    @PutMapping(value = ["/{task_id}"], consumes = [MediaType.APPLICATION_JSON_VALUE], produces = [MediaType.APPLICATION_JSON_VALUE])
    @Operation(summary = "Replace task by ID (Full Replacement)")
    fun updateTask(
        @PathVariable("task_id") taskId: Long,
        @Valid @RequestBody request: TaskReplaceRequest
    ): TaskResponse {
        return taskService.replaceTask(taskId, request)
    }

    @PatchMapping(value = ["/{task_id}"], consumes = [MediaType.APPLICATION_JSON_VALUE], produces = [MediaType.APPLICATION_JSON_VALUE])
    @Operation(summary = "Partially update task by ID")
    fun patchTask(
        @PathVariable("task_id") taskId: Long,
        @RequestBody request: TaskUpdateRequest
    ): TaskResponse {
        return taskService.patchTask(taskId, request)
    }

    @DeleteMapping("/{task_id}")
    @ResponseStatus(HttpStatus.NO_CONTENT)
    @Operation(summary = "Delete task by ID")
    fun deleteTask(@PathVariable("task_id") taskId: Long) {
        taskService.deleteTask(taskId)
    }
}
