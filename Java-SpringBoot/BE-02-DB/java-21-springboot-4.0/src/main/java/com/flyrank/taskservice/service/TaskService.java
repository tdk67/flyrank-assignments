package com.flyrank.taskservice.service;

import com.flyrank.taskservice.dto.*;

import java.util.SequencedCollection;

/**
 * Service interface for Java 21 Task operations.
 */
public interface TaskService {
    SequencedCollection<TaskResponse> getAllTasks(String search, Boolean done);
    TaskResponse getTaskById(Long id);
    TaskResponse createTask(TaskCreateRequest request);
    TaskResponse replaceTask(Long id, TaskReplaceRequest request);
    TaskResponse patchTask(Long id, TaskUpdateRequest request);
    void deleteTask(Long id);
    StatsResponse getStats();
}
