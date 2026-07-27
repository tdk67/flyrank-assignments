package com.flyrank.userservice.dto

import com.fasterxml.jackson.annotation.JsonIgnore
import com.fasterxml.jackson.annotation.JsonProperty
import com.fasterxml.jackson.databind.PropertyNamingStrategies
import com.fasterxml.jackson.databind.annotation.JsonNaming
import io.swagger.v3.oas.annotations.media.Schema
import jakarta.validation.constraints.NotBlank

/**
 * A user's name data class. Both first_name and last_name are required.
 */
@Schema(description = "User's first and last name object")
@JsonNaming(PropertyNamingStrategies.SnakeCaseStrategy::class)
data class NameDto(
    @field:Schema(description = "First name", example = "Jane")
    @field:NotBlank(message = "first_name is required and cannot be blank")
    @param:JsonProperty("first_name")
    @get:JsonProperty("first_name")
    val firstName: String,

    @field:Schema(description = "Last name", example = "Doe")
    @field:NotBlank(message = "last_name is required and cannot be blank")
    @param:JsonProperty("last_name")
    @get:JsonProperty("last_name")
    val lastName: String
) {
    @get:JsonIgnore
    val fullName: String
        get() = "$firstName $lastName"
}
