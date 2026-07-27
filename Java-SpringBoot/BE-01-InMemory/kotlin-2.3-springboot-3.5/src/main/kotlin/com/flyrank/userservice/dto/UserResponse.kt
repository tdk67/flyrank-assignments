package com.flyrank.userservice.dto

import io.swagger.v3.oas.annotations.media.Schema
import java.util.UUID

/**
 * A stored user record returned by POST /user and GET /user/{user_id}.
 */
@Schema(description = "User record object")
data class UserResponse(
    @field:Schema(description = "Server-generated unique user id", example = "a1b2c3d4-e5f6-7a8b-9c0d-1e2f3a4b5c6d")
    val id: UUID,

    @field:Schema(description = "User name object")
    val name: NameDto,

    @field:Schema(description = "Email address", example = "jane.doe@example.com")
    val email: String? = null,

    @field:Schema(description = "Telephone number", example = "+1-555-0199")
    val telephone: String? = null
)
