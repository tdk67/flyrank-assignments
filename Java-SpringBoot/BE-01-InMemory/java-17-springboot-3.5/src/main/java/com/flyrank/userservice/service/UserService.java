package com.flyrank.userservice.service;

import com.flyrank.userservice.dto.UserCreateRequest;
import com.flyrank.userservice.dto.UserResponse;

import java.util.UUID;

/**
 * Service layer interface defining business operations for Users.
 */
public interface UserService {
    /**
     * Creates a new user with a generated UUID.
     */
    UserResponse createUser(UserCreateRequest request);

    /**
     * Retrieves an existing user by ID or throws UserNotFoundException.
     */
    UserResponse getUserById(UUID id);
}
