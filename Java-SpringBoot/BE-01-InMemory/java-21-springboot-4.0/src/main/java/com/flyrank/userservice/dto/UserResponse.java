package com.flyrank.userservice.dto;

import io.swagger.v3.oas.annotations.media.Schema;

import java.util.UUID;

/**
 * A stored user record returned by POST /user and GET /user/{user_id}.
 */
@Schema(description = "User record object")
public record UserResponse(
        @Schema(description = "Server-generated unique user id", example = "a1b2c3d4-e5f6-7a8b-9c0d-1e2f3a4b5c6d")
        UUID id,

        @Schema(description = "User name object")
        NameDto name,

        @Schema(description = "Email address", example = "jane.doe@example.com")
        String email,

        @Schema(description = "Telephone number", example = "+1-555-0199")
        String telephone
) {}
