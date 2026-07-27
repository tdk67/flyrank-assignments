package com.flyrank.userservice.service

import com.flyrank.userservice.dto.UserCreateRequest
import com.flyrank.userservice.dto.UserResponse
import java.util.UUID

/**
 * Service layer interface in Kotlin.
 */
interface UserService {
    fun createUser(request: UserCreateRequest): UserResponse
    fun getUserById(id: UUID): UserResponse
}
