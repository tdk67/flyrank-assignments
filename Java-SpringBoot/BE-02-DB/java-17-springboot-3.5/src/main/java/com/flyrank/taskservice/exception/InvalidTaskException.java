package com.flyrank.taskservice.exception;

/**
 * Thrown when task input or title is invalid/blank.
 */
public class InvalidTaskException extends RuntimeException {
    public InvalidTaskException(String message) {
        super(message);
    }
}
