package com.flyrank.taskservice.exception;

/**
 * Thrown when a task is not found by ID.
 */
public class TaskNotFoundException extends RuntimeException {
    public TaskNotFoundException(Long taskId) {
        super(String.format("Task with id '%d' not found", taskId));
    }
}
