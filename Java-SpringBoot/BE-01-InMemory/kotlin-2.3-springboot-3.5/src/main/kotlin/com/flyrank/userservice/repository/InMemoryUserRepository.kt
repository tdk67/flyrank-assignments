package com.flyrank.userservice.repository

import com.flyrank.userservice.dto.UserResponse
import org.springframework.stereotype.Repository
import java.util.UUID
import java.util.concurrent.ConcurrentHashMap

/**
 * Thread-safe In-Memory UserRepository implementation in Kotlin using ConcurrentHashMap.
 */
@Repository
class InMemoryUserRepository : UserRepository {

    private val userStore = ConcurrentHashMap<UUID, UserResponse>()

    override fun save(user: UserResponse): UserResponse {
        userStore[user.id] = user
        return user
    }

    override fun findById(id: UUID): UserResponse? {
        return userStore[id]
    }

    override fun findAll(): List<UserResponse> {
        return userStore.values.toList()
    }
}
