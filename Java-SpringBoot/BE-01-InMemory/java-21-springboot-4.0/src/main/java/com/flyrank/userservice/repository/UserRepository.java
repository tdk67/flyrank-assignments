package com.flyrank.userservice.repository;

import com.flyrank.userservice.dto.UserResponse;

import java.util.Optional;
import java.util.SequencedCollection;
import java.util.UUID;

/**
 * Java 21 Repository interface showcasing SequencedCollection for ordered retrieval.
 */
public interface UserRepository {
    UserResponse save(UserResponse user);

    Optional<UserResponse> findById(UUID id);

    /**
     * Java 21 SequencedCollection interface returning stored users in insertion order.
     */
    SequencedCollection<UserResponse> findAllSequenced();
}
