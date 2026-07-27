package com.flyrank.userservice.exception

import com.flyrank.userservice.dto.ErrorResponse
import org.springframework.http.HttpStatus
import org.springframework.http.ResponseEntity
import org.springframework.http.converter.HttpMessageNotReadableException
import org.springframework.validation.FieldError
import org.springframework.web.bind.MethodArgumentNotValidException
import org.springframework.web.bind.annotation.ExceptionHandler
import org.springframework.web.bind.annotation.RestControllerAdvice

/**
 * Controller Advice in idiomatic Kotlin utilizing pattern matching when expressions.
 */
@RestControllerAdvice
class GlobalExceptionHandler {

    @ExceptionHandler(UserNotFoundException::class)
    fun handleUserNotFound(ex: UserNotFoundException): ResponseEntity<ErrorResponse> {
        return ResponseEntity
            .status(HttpStatus.NOT_FOUND)
            .body(ErrorResponse(ex.message ?: "User not found"))
    }

    @ExceptionHandler(MethodArgumentNotValidException::class)
    fun handleValidationErrors(ex: MethodArgumentNotValidException): ResponseEntity<ErrorResponse> {
        val detail = ex.bindingResult.fieldErrors
            .joinToString("; ") { formatFieldError(it) }

        return ResponseEntity
            .status(HttpStatus.UNPROCESSABLE_ENTITY)
            .body(ErrorResponse(detail))
    }

    @ExceptionHandler(HttpMessageNotReadableException::class)
    fun handleHttpMessageNotReadable(ex: HttpMessageNotReadableException): ResponseEntity<ErrorResponse> {
        val message = ex.message ?: ""

        // Kotlin 2.1+ when expression with boolean conditions (guards)
        val errorDetail = when {
            message.contains("Unrecognized field") -> "Unrecognized or forbidden field present in JSON payload"
            message.contains("JSON parse error") -> "Malformed JSON syntax payload"
            else -> "Invalid JSON request body payload"
        }

        return ResponseEntity
            .status(HttpStatus.UNPROCESSABLE_ENTITY)
            .body(ErrorResponse(errorDetail))
    }

    private fun formatFieldError(fieldError: FieldError): String {
        val field = fieldError.field
        val formattedField = field.replace(Regex("([a-z])([A-Z])"), "$1_$2").lowercase()
        return "$formattedField: ${fieldError.defaultMessage}"
    }
}
