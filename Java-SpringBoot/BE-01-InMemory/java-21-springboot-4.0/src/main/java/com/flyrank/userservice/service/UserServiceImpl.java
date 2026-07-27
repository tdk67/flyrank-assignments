package com.flyrank.userservice.service;

import com.flyrank.userservice.dto.NameDto;
import com.flyrank.userservice.dto.UserCreateRequest;
import com.flyrank.userservice.dto.UserResponse;
import com.flyrank.userservice.exception.UserNotFoundException;
import com.flyrank.userservice.repository.UserRepository;
import org.springframework.stereotype.Service;

import java.util.SequencedCollection;
import java.util.UUID;

/**
 * Business logic implementation for UserService utilizing Java 21 Record Patterns.
 */
@Service
public class UserServiceImpl implements UserService {

    private final UserRepository userRepository;

    public UserServiceImpl(UserRepository userRepository) {
        this.userRepository = userRepository;
    }

    @Override
    public UserResponse createUser(UserCreateRequest request) {
        UUID newId = UUID.randomUUID();

        // Java 21 Record Pattern Deconstruction in pattern matching:
        // Automatically extracts nested `name`, `email`, and `telephone` components from `UserCreateRequest`
        if (request instanceof UserCreateRequest(NameDto name, String email, String telephone)) {
            UserResponse newRecord = new UserResponse(newId, name, email, telephone);
            return userRepository.save(newRecord);
        }

        // Fallback
        UserResponse fallbackRecord = new UserResponse(
                newId,
                request.name(),
                request.email(),
                request.telephone()
        );
        return userRepository.save(fallbackRecord);
    }

    @Override
    public UserResponse getUserById(UUID id) {
        return userRepository.findById(id)
                .orElseThrow(() -> new UserNotFoundException(id));
    }

    @Override
    public SequencedCollection<UserResponse> getAllUsers() {
        return userRepository.findAllSequenced();
    }
}
