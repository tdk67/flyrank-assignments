package com.flyrank.userservice.repository

import com.flyrank.userservice.dto.UserResponse
import java.util.UUID

/**
 * Repository interface using idiomatic Kotlin functions.
 */
interface UserRepository {
    fun save(user: UserResponse): UserResponse
    fun findById(id: UUID): UserResponse?
    fun findAll(): List<UserResponse>
}
