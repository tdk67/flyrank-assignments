package com.flyrank.userservice.repository;

import com.flyrank.userservice.dto.UserResponse;

import java.util.Optional;
import java.util.UUID;

/**
 * Repository interface for User data access.
 */
public interface UserRepository {
    /**
     * Save a user record.
     */
    UserResponse save(UserResponse user);

    /**
     * Find a user record by unique ID.
     */
    Optional<UserResponse> findById(UUID id);
}
