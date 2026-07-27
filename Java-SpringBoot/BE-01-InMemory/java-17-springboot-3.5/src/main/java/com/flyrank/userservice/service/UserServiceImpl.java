package com.flyrank.userservice.service;

import com.flyrank.userservice.dto.UserCreateRequest;
import com.flyrank.userservice.dto.UserResponse;
import com.flyrank.userservice.exception.UserNotFoundException;
import com.flyrank.userservice.repository.UserRepository;
import org.springframework.stereotype.Service;

import java.util.UUID;

/**
 * Business logic implementation for UserService.
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
        UserResponse newRecord = new UserResponse(
                newId,
                request.name(),
                request.email(),
                request.telephone()
        );
        return userRepository.save(newRecord);
    }

    @Override
    public UserResponse getUserById(UUID id) {
        return userRepository.findById(id)
                .orElseThrow(() -> new UserNotFoundException(id));
    }
}
