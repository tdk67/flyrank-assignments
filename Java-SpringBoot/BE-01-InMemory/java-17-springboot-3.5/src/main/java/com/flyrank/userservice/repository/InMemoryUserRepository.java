package com.flyrank.userservice.repository;

import com.flyrank.userservice.dto.UserResponse;
import org.springframework.stereotype.Repository;

import java.util.Map;
import java.util.Optional;
import java.util.UUID;
import java.util.concurrent.ConcurrentHashMap;

/**
 * Thread-safe In-Memory UserRepository implementation using ConcurrentHashMap.
 * Data is cleared when the application restarts.
 */
@Repository
public class InMemoryUserRepository implements UserRepository {

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
}
