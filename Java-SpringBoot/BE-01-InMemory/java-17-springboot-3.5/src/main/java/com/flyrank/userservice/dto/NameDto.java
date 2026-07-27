package com.flyrank.userservice.dto;

import com.fasterxml.jackson.annotation.JsonProperty;
import io.swagger.v3.oas.annotations.media.Schema;
import jakarta.validation.constraints.NotBlank;

/**
 * A user's name record. Both first_name and last_name are required when a name is supplied.
 */
@Schema(description = "User's first and last name object")
public record NameDto(
        @Schema(description = "First name", example = "Jane")
        @NotBlank(message = "first_name is required and cannot be blank")
        @JsonProperty("first_name")
        String firstName,

        @Schema(description = "Last name", example = "Doe")
        @NotBlank(message = "last_name is required and cannot be blank")
        @JsonProperty("last_name")
        String lastName
) {}
