package com.flyrank.userservice.dto;

import io.swagger.v3.oas.annotations.media.Schema;
import jakarta.validation.Valid;
import jakarta.validation.constraints.Email;
import jakarta.validation.constraints.NotNull;

/**
 * Payload accepted by POST /user. Only name is mandatory.
 */
@Schema(description = "User creation request payload")
public record UserCreateRequest(
        @Schema(description = "User's first and last name (mandatory)", requiredMode = Schema.RequiredMode.REQUIRED)
        @NotNull(message = "name object is required")
        @Valid
        NameDto name,

        @Schema(description = "Email address (optional)", example = "jane.doe@example.com")
        @Email(message = "value is not a valid email address")
        String email,

        @Schema(description = "Telephone number (optional)", example = "+1-555-0199")
        String telephone
) {}
