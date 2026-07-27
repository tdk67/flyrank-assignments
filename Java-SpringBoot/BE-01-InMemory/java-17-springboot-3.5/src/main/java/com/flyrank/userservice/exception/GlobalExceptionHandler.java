package com.flyrank.userservice.exception;

import com.flyrank.userservice.dto.ErrorResponse;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.http.converter.HttpMessageNotReadableException;
import org.springframework.validation.FieldError;
import org.springframework.web.bind.MethodArgumentNotValidException;
import org.springframework.web.bind.annotation.ExceptionHandler;
import org.springframework.web.bind.annotation.RestControllerAdvice;

import java.util.stream.Collectors;

/**
 * Controller Advice that intercepts exceptions and formats them as standard ErrorResponse objects,
 * matching FastAPI HTTP status codes and JSON formats (404 and 422).
 */
@RestControllerAdvice
public class GlobalExceptionHandler {

    /**
     * Handle 404 User Not Found exception.
     */
    @ExceptionHandler(UserNotFoundException.class)
    public ResponseEntity<ErrorResponse> handleUserNotFound(UserNotFoundException ex) {
        return ResponseEntity
                .status(HttpStatus.NOT_FOUND)
                .body(new ErrorResponse(ex.getMessage()));
    }

    /**
     * Handle 422 Bean Validation errors (missing mandatory fields, invalid email format, etc.).
     */
    @ExceptionHandler(MethodArgumentNotValidException.class)
    public ResponseEntity<ErrorResponse> handleValidationErrors(MethodArgumentNotValidException ex) {
        String detail = ex.getBindingResult().getFieldErrors().stream()
                .map(this::formatFieldError)
                .collect(Collectors.joining("; "));

        return ResponseEntity
                .status(HttpStatus.UNPROCESSABLE_ENTITY)
                .body(new ErrorResponse(detail));
    }

    /**
     * Handle 422 JSON parsing errors (malformed JSON or unknown fields when extra="forbid").
     */
    @ExceptionHandler(HttpMessageNotReadableException.class)
    public ResponseEntity<ErrorResponse> handleHttpMessageNotReadable(HttpMessageNotReadableException ex) {
        String message = ex.getMessage();
        if (message != null && message.contains("Unrecognized field")) {
            // Extract unrecognized field name cleanly if possible
            return ResponseEntity
                    .status(HttpStatus.UNPROCESSABLE_ENTITY)
                    .body(new ErrorResponse("Unrecognized or forbidden field present in JSON payload"));
        }

        return ResponseEntity
                .status(HttpStatus.UNPROCESSABLE_ENTITY)
                .body(new ErrorResponse("Invalid JSON request body payload"));
    }

    private String formatFieldError(FieldError fieldError) {
        String field = fieldError.getField();
        // Convert camelCase to snake_case for field path readability matching Python
        String formattedField = field.replaceAll("([a-z])([A-Z])", "$1_$2").toLowerCase();
        return formattedField + ": " + fieldError.getDefaultMessage();
    }
}
