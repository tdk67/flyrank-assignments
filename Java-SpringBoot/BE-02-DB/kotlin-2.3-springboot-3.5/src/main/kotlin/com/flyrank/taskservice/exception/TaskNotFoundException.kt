package com.flyrank.taskservice.exception

class TaskNotFoundException(taskId: Long) : RuntimeException("Task with id '$taskId' not found")
