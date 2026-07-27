package com.flyrank.taskservice.service

import com.flyrank.taskservice.dto.*
import com.flyrank.taskservice.entity.TaskEntity
import com.flyrank.taskservice.exception.InvalidTaskException
import com.flyrank.taskservice.exception.TaskNotFoundException
import com.flyrank.taskservice.repository.TaskRepository
import org.springframework.stereotype.Service
import org.springframework.transaction.annotation.Transactional

@Service
class TaskServiceImpl(
    private val taskRepository: TaskRepository
) : TaskService {

    @Transactional(readOnly = true)
    override fun getAllTasks(search: String?, done: Boolean?): List<TaskResponse> {
        return taskRepository.filterTasks(search, done).map { toResponse(it) }
    }

    @Transactional(readOnly = true)
    override fun getTaskById(id: Long): TaskResponse {
        val entity = taskRepository.findById(id).orElseThrow { TaskNotFoundException(id) }
        return toResponse(entity)
    }

    @Transactional
    override fun createTask(request: TaskCreateRequest): TaskResponse {
        val title = request.title?.trim()
        if (title.isNullOrEmpty()) {
            throw InvalidTaskException("Task title cannot be empty")
        }
        val entity = TaskEntity(title = title, done = false)
        val saved = taskRepository.save(entity)
        return toResponse(saved)
    }

    @Transactional
    override fun replaceTask(id: Long, request: TaskReplaceRequest): TaskResponse {
        val entity = taskRepository.findById(id).orElseThrow { TaskNotFoundException(id) }

        val title = request.title?.trim()
        if (title.isNullOrEmpty()) {
            throw InvalidTaskException("Task title cannot be empty")
        }
        val done = request.done ?: throw InvalidTaskException("done status is required for PUT full replacement")

        entity.title = title
        entity.done = done
        val saved = taskRepository.save(entity)
        return toResponse(saved)
    }

    @Transactional
    override fun patchTask(id: Long, request: TaskUpdateRequest): TaskResponse {
        val entity = taskRepository.findById(id).orElseThrow { TaskNotFoundException(id) }

        request.title?.let {
            val trimmed = it.trim()
            if (trimmed.isEmpty()) {
                throw InvalidTaskException("Task title cannot be empty")
            }
            entity.title = trimmed
        }

        request.done?.let {
            entity.done = it
        }

        val saved = taskRepository.save(entity)
        return toResponse(saved)
    }

    @Transactional
    override fun deleteTask(id: Long) {
        val entity = taskRepository.findById(id).orElseThrow { TaskNotFoundException(id) }
        taskRepository.delete(entity)
    }

    @Transactional(readOnly = true)
    override fun getStats(): StatsResponse {
        val total = taskRepository.count()
        val done = taskRepository.countByDone(true)
        val open = total - done
        return StatsResponse(listOf("TASKS", "FLYWAY_SCHEMA_HISTORY"), total, done, open)
    }

    private fun toResponse(entity: TaskEntity): TaskResponse {
        return TaskResponse(
            id = requireNotNull(entity.id) { "Entity ID cannot be null" },
            title = entity.title,
            done = entity.done,
            createdAt = entity.createdAt,
            updatedAt = entity.updatedAt
        )
    }
}
