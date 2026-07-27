package com.flyrank.userservice.controller

import com.flyrank.userservice.dto.ErrorResponse
import com.flyrank.userservice.dto.UserCreateRequest
import com.flyrank.userservice.dto.UserResponse
import com.flyrank.userservice.service.UserService
import io.swagger.v3.oas.annotations.Operation
import io.swagger.v3.oas.annotations.media.Content
import io.swagger.v3.oas.annotations.media.Schema
import io.swagger.v3.oas.annotations.responses.ApiResponse
import io.swagger.v3.oas.annotations.responses.ApiResponses
import io.swagger.v3.oas.annotations.tags.Tag
import jakarta.validation.Valid
import org.springframework.http.HttpStatus
import org.springframework.http.MediaType
import org.springframework.web.bind.annotation.*
import java.util.UUID

/**
 * REST Controller in Kotlin exposing user endpoints.
 */
@RestController
@RequestMapping
@Tag(name = "users", description = "User Management Endpoints (Kotlin 2.3 & K2 Compiler)")
class UserController(
    private val userService: UserService
) {

    @PostMapping(
        value = ["/user"],
        consumes = [MediaType.APPLICATION_JSON_VALUE],
        produces = [MediaType.APPLICATION_JSON_VALUE]
    )
    @ResponseStatus(HttpStatus.CREATED)
    @Operation(summary = "Create a new user", description = "Creates a user from the given payload and returns the stored record, including its new id.")
    @ApiResponses(
        value = [
            ApiResponse(
                responseCode = "201",
                description = "User created successfully",
                content = [Content(mediaType = MediaType.APPLICATION_JSON_VALUE, schema = Schema(implementation = UserResponse::class))]
            ),
            ApiResponse(
                responseCode = "422",
                description = "Invalid request payload or forbidden extra fields",
                content = [Content(mediaType = MediaType.APPLICATION_JSON_VALUE, schema = Schema(implementation = ErrorResponse::class))]
            )
        ]
    )
    fun createUser(@Valid @RequestBody request: UserCreateRequest): UserResponse {
        return userService.createUser(request)
    }

    @GetMapping(
        value = ["/user/{user_id}"],
        produces = [MediaType.APPLICATION_JSON_VALUE]
    )
    @ResponseStatus(HttpStatus.OK)
    @Operation(summary = "Retrieve a user by id", description = "Return the user matching user_id, or a 404 error if it does not exist.")
    @ApiResponses(
        value = [
            ApiResponse(
                responseCode = "200",
                description = "User found",
                content = [Content(mediaType = MediaType.APPLICATION_JSON_VALUE, schema = Schema(implementation = UserResponse::class))]
            ),
            ApiResponse(
                responseCode = "404",
                description = "User not found",
                content = [Content(mediaType = MediaType.APPLICATION_JSON_VALUE, schema = Schema(implementation = ErrorResponse::class))]
            )
        ]
    )
    fun getUser(@PathVariable("user_id") userId: UUID): UserResponse {
        return userService.getUserById(userId)
    }
}
