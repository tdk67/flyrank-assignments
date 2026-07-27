package com.flyrank.userservice.controller;

import com.flyrank.userservice.dto.ErrorResponse;
import com.flyrank.userservice.dto.UserCreateRequest;
import com.flyrank.userservice.dto.UserResponse;
import com.flyrank.userservice.service.UserService;
import io.swagger.v3.oas.annotations.Operation;
import io.swagger.v3.oas.annotations.media.Content;
import io.swagger.v3.oas.annotations.media.Schema;
import io.swagger.v3.oas.annotations.responses.ApiResponse;
import io.swagger.v3.oas.annotations.responses.ApiResponses;
import io.swagger.v3.oas.annotations.tags.Tag;
import jakarta.validation.Valid;
import org.springframework.http.HttpStatus;
import org.springframework.http.MediaType;
import org.springframework.web.bind.annotation.*;

import java.util.UUID;

/**
 * REST Controller exposing user management endpoints for Java 21 & Spring Boot 4.0 platform.
 */
@RestController
@RequestMapping
@Tag(name = "users", description = "User Management Endpoints (Java 21 & Virtual Threads)")
public class UserController {

    private final UserService userService;

    public UserController(UserService userService) {
        this.userService = userService;
    }

    /**
     * Create a new user from the given payload and return the stored record, including its new ID.
     */
    @PostMapping(
            value = "/user",
            consumes = MediaType.APPLICATION_JSON_VALUE,
            produces = MediaType.APPLICATION_JSON_VALUE
    )
    @ResponseStatus(HttpStatus.CREATED)
    @Operation(summary = "Create a new user", description = "Creates a user from the given payload and returns the stored record, including its new id.")
    @ApiResponses(value = {
            @ApiResponse(
                    responseCode = "201",
                    description = "User created successfully",
                    content = @Content(mediaType = MediaType.APPLICATION_JSON_VALUE, schema = @Schema(implementation = UserResponse.class))
            ),
            @ApiResponse(
                    responseCode = "422",
                    description = "Invalid request payload or forbidden extra fields",
                    content = @Content(mediaType = MediaType.APPLICATION_JSON_VALUE, schema = @Schema(implementation = ErrorResponse.class))
            )
    })
    public UserResponse createUser(@Valid @RequestBody UserCreateRequest request) {
        return userService.createUser(request);
    }

    /**
     * Return the user matching user_id, or a 404 error if it does not exist.
     */
    @GetMapping(
            value = "/user/{user_id}",
            produces = MediaType.APPLICATION_JSON_VALUE
    )
    @ResponseStatus(HttpStatus.OK)
    @Operation(summary = "Retrieve a user by id", description = "Return the user matching user_id, or a 404 error if it does not exist.")
    @ApiResponses(value = {
            @ApiResponse(
                    responseCode = "200",
                    description = "User found",
                    content = @Content(mediaType = MediaType.APPLICATION_JSON_VALUE, schema = @Schema(implementation = UserResponse.class))
            ),
            @ApiResponse(
                    responseCode = "404",
                    description = "User not found",
                    content = @Content(mediaType = MediaType.APPLICATION_JSON_VALUE, schema = @Schema(implementation = ErrorResponse.class))
            )
    })
    public UserResponse getUser(@PathVariable("user_id") UUID userId) {
        return userService.getUserById(userId);
    }
}
