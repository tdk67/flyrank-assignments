package com.flyrank.taskservice.entity

import jakarta.persistence.*
import java.time.LocalDateTime
import java.time.format.DateTimeFormatter

/**
 * JPA Entity in Kotlin representing a task record persisted in the database.
 */
@Entity
@Table(name = "tasks")
class TaskEntity(
    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    var id: Long? = null,

    @Column(nullable = false)
    var title: String = "",

    @Column(nullable = false)
    var done: Boolean = false,

    @Column(name = "created_at", nullable = false, updatable = false)
    var createdAt: String? = null,

    @Column(name = "updated_at", nullable = false)
    var updatedAt: String? = null
) {
    @PrePersist
    fun onCreate() {
        val nowStr = LocalDateTime.now().format(DateTimeFormatter.ISO_DATE_TIME)
        if (createdAt == null) {
            createdAt = nowStr
        }
        updatedAt = nowStr
    }

    @PreUpdate
    fun onUpdate() {
        updatedAt = LocalDateTime.now().format(DateTimeFormatter.ISO_DATE_TIME)
    }
}
