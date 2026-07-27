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
 * Controller Advice utilizing Java 21 Features to format exceptions cleanly.
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
     * Handle 422 Bean Validation errors.
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
     * Handle 422 JSON parsing errors using Java 21 Pattern Matching for switch!
     */
    @ExceptionHandler(HttpMessageNotReadableException.class)
    public ResponseEntity<ErrorResponse> handleHttpMessageNotReadable(HttpMessageNotReadableException ex) {
        String message = ex.getMessage();

        // Java 21 Pattern Matching for switch with null check & guard expressions
        String errorDetail = switch (message) {
            case String msg when msg.contains("Unrecognized field") ->
                    "Unrecognized or forbidden field present in JSON payload";
            case String msg when msg.contains("JSON parse error") ->
                    "Malformed JSON syntax payload";
            case null ->
                    "Invalid JSON request body payload";
            default ->
                    "Invalid JSON request body payload";
        };

        return ResponseEntity
                .status(HttpStatus.UNPROCESSABLE_ENTITY)
                .body(new ErrorResponse(errorDetail));
    }

    private String formatFieldError(FieldError fieldError) {
        String field = fieldError.getField();
        String formattedField = field.replaceAll("([a-z])([A-Z])", "$1_$2").toLowerCase();
        return formattedField + ": " + fieldError.getDefaultMessage();
    }
}
