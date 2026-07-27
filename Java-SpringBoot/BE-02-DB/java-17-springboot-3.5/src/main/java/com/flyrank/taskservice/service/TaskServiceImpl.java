package com.flyrank.taskservice.service;

import com.flyrank.taskservice.dto.*;
import com.flyrank.taskservice.entity.TaskEntity;
import com.flyrank.taskservice.exception.InvalidTaskException;
import com.flyrank.taskservice.exception.TaskNotFoundException;
import com.flyrank.taskservice.repository.TaskRepository;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.util.List;

/**
 * Service implementation managing task business rules and database persistence.
 */
@Service
public class TaskServiceImpl implements TaskService {

    private final TaskRepository taskRepository;

    public TaskServiceImpl(TaskRepository taskRepository) {
        this.taskRepository = taskRepository;
    }

    @Override
    @Transactional(readOnly = true)
    public List<TaskResponse> getAllTasks(String search, Boolean done) {
        return taskRepository.filterTasks(search, done).stream()
                .map(this::toResponse)
                .toList();
    }

    @Override
    @Transactional(readOnly = true)
    public TaskResponse getTaskById(Long id) {
        TaskEntity entity = taskRepository.findById(id)
                .orElseThrow(() -> new TaskNotFoundException(id));
        return toResponse(entity);
    }

    @Override
    @Transactional
    public TaskResponse createTask(TaskCreateRequest request) {
        if (request.title() == null || request.title().trim().isEmpty()) {
            throw new InvalidTaskException("Task title cannot be empty");
        }
        TaskEntity entity = new TaskEntity(request.title().trim(), false);
        TaskEntity saved = taskRepository.save(entity);
        return toResponse(saved);
    }

    @Override
    @Transactional
    public TaskResponse replaceTask(Long id, TaskReplaceRequest request) {
        TaskEntity entity = taskRepository.findById(id)
                .orElseThrow(() -> new TaskNotFoundException(id));

        if (request.title() == null || request.title().trim().isEmpty()) {
            throw new InvalidTaskException("Task title cannot be empty");
        }

        entity.setTitle(request.title().trim());
        entity.setDone(request.done());
        TaskEntity saved = taskRepository.save(entity);
        return toResponse(saved);
    }

    @Override
    @Transactional
    public TaskResponse patchTask(Long id, TaskUpdateRequest request) {
        TaskEntity entity = taskRepository.findById(id)
                .orElseThrow(() -> new TaskNotFoundException(id));

        if (request.title() != null) {
            if (request.title().trim().isEmpty()) {
                throw new InvalidTaskException("Task title cannot be empty");
            }
            entity.setTitle(request.title().trim());
        }

        if (request.done() != null) {
            entity.setDone(request.done());
        }

        TaskEntity saved = taskRepository.save(entity);
        return toResponse(saved);
    }

    @Override
    @Transactional
    public void deleteTask(Long id) {
        TaskEntity entity = taskRepository.findById(id)
                .orElseThrow(() -> new TaskNotFoundException(id));
        taskRepository.delete(entity);
    }

    @Override
    @Transactional(readOnly = true)
    public StatsResponse getStats() {
        long total = taskRepository.count();
        long done = taskRepository.countByDone(true);
        long open = total - done;
        return new StatsResponse(List.of("TASKS", "FLYWAY_SCHEMA_HISTORY"), total, done, open);
    }

    private TaskResponse toResponse(TaskEntity entity) {
        return new TaskResponse(
                entity.getId(),
                entity.getTitle(),
                entity.isDone(),
                entity.getCreatedAt(),
                entity.getUpdatedAt()
        );
    }
}
