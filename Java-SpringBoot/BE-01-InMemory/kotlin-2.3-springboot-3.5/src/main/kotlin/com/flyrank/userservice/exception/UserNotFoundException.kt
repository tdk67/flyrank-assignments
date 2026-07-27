package com.flyrank.userservice.exception

import java.util.UUID

/**
 * Exception thrown when a user ID does not exist in storage.
 */
class UserNotFoundException(userId: UUID) : RuntimeException("User with id '$userId' not found")
