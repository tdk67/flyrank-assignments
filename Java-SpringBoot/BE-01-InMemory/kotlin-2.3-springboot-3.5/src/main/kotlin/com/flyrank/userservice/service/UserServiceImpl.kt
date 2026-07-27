package com.flyrank.userservice.service

import com.flyrank.userservice.dto.UserCreateRequest
import com.flyrank.userservice.dto.UserResponse
import com.flyrank.userservice.exception.UserNotFoundException
import com.flyrank.userservice.repository.UserRepository
import org.springframework.stereotype.Service
import java.util.UUID

/**
 * Business logic implementation in idiomatic Kotlin.
 */
@Service
class UserServiceImpl(
    private val userRepository: UserRepository
) : UserService {

    override fun createUser(request: UserCreateRequest): UserResponse {
        val newId = UUID.randomUUID()
        val nameDto = requireNotNull(request.name) { "name object is required" }

        val newRecord = UserResponse(
            id = newId,
            name = nameDto,
            email = request.email,
            telephone = request.telephone
        )
        return userRepository.save(newRecord)
    }

    override fun getUserById(id: UUID): UserResponse {
        return userRepository.findById(id) ?: throw UserNotFoundException(id)
    }
}
