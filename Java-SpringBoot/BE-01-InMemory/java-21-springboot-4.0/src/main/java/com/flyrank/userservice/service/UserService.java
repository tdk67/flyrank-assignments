package com.flyrank.userservice.service;

import com.flyrank.userservice.dto.UserCreateRequest;
import com.flyrank.userservice.dto.UserResponse;

import java.util.SequencedCollection;
import java.util.UUID;

/**
 * Service layer interface defining business operations for Users.
 */
public interface UserService {
    UserResponse createUser(UserCreateRequest request);

    UserResponse getUserById(UUID id);

    SequencedCollection<UserResponse> getAllUsers();
}
