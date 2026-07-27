package com.flyrank.userservice.repository;

import com.flyrank.userservice.dto.UserResponse;
import org.springframework.stereotype.Repository;

import java.util.*;
import java.util.concurrent.ConcurrentHashMap;

/**
 * Thread-safe In-Memory UserRepository implementation using ConcurrentHashMap and LinkedHashMap for SequencedCollection support.
 */
@Repository
public class InMemoryUserRepository implements UserRepository {

    // ConcurrentHashMap for fast thread-safe UUID lookup
    private final Map<UUID, UserResponse> userStore = new ConcurrentHashMap<>();

    @Override
    public UserResponse save(UserResponse user) {
        userStore.put(user.id(), user);
        return user;
    }

    @Override
    public Optional<UserResponse> findById(UUID id) {
        return Optional.ofNullable(userStore.get(id));
    }

    @Override
    public SequencedCollection<UserResponse> findAllSequenced() {
        // Java 21 SequencedCollection interface
        return new ArrayList<>(userStore.values());
    }
}
