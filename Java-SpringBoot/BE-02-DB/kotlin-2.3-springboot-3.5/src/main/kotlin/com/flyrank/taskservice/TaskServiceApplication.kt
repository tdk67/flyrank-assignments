package com.flyrank.taskservice

import com.flyrank.taskservice.entity.TaskEntity
import com.flyrank.taskservice.repository.TaskRepository
import org.springframework.boot.CommandLineRunner
import org.springframework.boot.autoconfigure.SpringBootApplication
import org.springframework.boot.runApplication
import org.springframework.context.annotation.Bean

@SpringBootApplication
class TaskServiceApplication {

    @Bean
    fun seedDatabase(repository: TaskRepository) = CommandLineRunner {
        if (repository.count() == 0L) {
            repository.saveAll(
                listOf(
                    TaskEntity(title = "Buy groceries", done = false),
                    TaskEntity(title = "Complete Flyrank assignment BE-02 in Kotlin", done = true),
                    TaskEntity(title = "Explore Kotlin 2.3 & Spring Data JPA", done = false)
                )
            )
        }
    }
}

fun main(args: Array<String>) {
    runApplication<TaskServiceApplication>(*args)
}
