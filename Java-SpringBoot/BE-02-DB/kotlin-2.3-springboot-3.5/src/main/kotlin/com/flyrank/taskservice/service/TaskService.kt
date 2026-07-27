package com.flyrank.taskservice.service

import com.flyrank.taskservice.dto.*

interface TaskService {
    fun getAllTasks(search: String?, done: Boolean?): List<TaskResponse>
    fun getTaskById(id: Long): TaskResponse
    fun createTask(request: TaskCreateRequest): TaskResponse
    fun replaceTask(id: Long, request: TaskReplaceRequest): TaskResponse
    fun patchTask(id: Long, request: TaskUpdateRequest): TaskResponse
    fun deleteTask(id: Long)
    fun getStats(): StatsResponse
}
