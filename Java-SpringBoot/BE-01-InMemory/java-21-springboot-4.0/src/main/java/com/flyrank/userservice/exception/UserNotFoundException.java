package com.flyrank.userservice.exception;

import java.util.UUID;

/**
 * Exception thrown when a user ID does not exist in storage.
 */
public class UserNotFoundException extends RuntimeException {
    public UserNotFoundException(UUID userId) {
        super(String.format("User with id '%s' not found", userId));
    }
}
