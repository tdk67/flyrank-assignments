package com.flyrank.taskservice.service;

import com.flyrank.taskservice.dto.*;
import com.flyrank.taskservice.entity.TaskEntity;
import com.flyrank.taskservice.exception.InvalidTaskException;
import com.flyrank.taskservice.exception.TaskNotFoundException;
import com.flyrank.taskservice.repository.TaskRepository;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.util.ArrayList;
import java.util.List;
import java.util.SequencedCollection;

/**
 * Service implementation managing task business rules utilizing Java 21 Record Patterns.
 */
@Service
public class TaskServiceImpl implements TaskService {

    private final TaskRepository taskRepository;

    public TaskServiceImpl(TaskRepository taskRepository) {
        this.taskRepository = taskRepository;
    }

    @Override
    @Transactional(readOnly = true)
    public SequencedCollection<TaskResponse> getAllTasks(String search, Boolean done) {
        SequencedCollection<TaskResponse> responses = new ArrayList<>();
        for (TaskEntity entity : taskRepository.filterTasksSequenced(search, done)) {
            responses.add(toResponse(entity));
        }
        return responses;
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
        if (request instanceof TaskCreateRequest(String title)) {
            if (title == null || title.trim().isEmpty()) {
                throw new InvalidTaskException("Task title cannot be empty");
            }
            TaskEntity entity = new TaskEntity(title.trim(), false);
            TaskEntity saved = taskRepository.save(entity);
            return toResponse(saved);
        }

        throw new InvalidTaskException("Invalid task request");
    }

    @Override
    @Transactional
    public TaskResponse replaceTask(Long id, TaskReplaceRequest request) {
        TaskEntity entity = taskRepository.findById(id)
                .orElseThrow(() -> new TaskNotFoundException(id));

        if (request instanceof TaskReplaceRequest(String title, Boolean done)) {
            if (title == null || title.trim().isEmpty()) {
                throw new InvalidTaskException("Task title cannot be empty");
            }
            entity.setTitle(title.trim());
            entity.setDone(done);
            TaskEntity saved = taskRepository.save(entity);
            return toResponse(saved);
        }

        throw new InvalidTaskException("Invalid replace request");
    }

    @Override
    @Transactional
    public TaskResponse patchTask(Long id, TaskUpdateRequest request) {
        TaskEntity entity = taskRepository.findById(id)
                .orElseThrow(() -> new TaskNotFoundException(id));

        if (request instanceof TaskUpdateRequest(String title, Boolean done)) {
            if (title != null) {
                if (title.trim().isEmpty()) {
                    throw new InvalidTaskException("Task title cannot be empty");
                }
                entity.setTitle(title.trim());
            }
            if (done != null) {
                entity.setDone(done);
            }
            TaskEntity saved = taskRepository.save(entity);
            return toResponse(saved);
        }

        throw new InvalidTaskException("Invalid patch request");
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
