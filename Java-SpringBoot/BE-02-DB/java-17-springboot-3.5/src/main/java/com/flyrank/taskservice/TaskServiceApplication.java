package com.flyrank.taskservice;

import com.flyrank.taskservice.entity.TaskEntity;
import com.flyrank.taskservice.repository.TaskRepository;
import org.springframework.boot.CommandLineRunner;
import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;
import org.springframework.context.annotation.Bean;

import java.util.List;

@SpringBootApplication
public class TaskServiceApplication {

    public static void main(String[] args) {
        SpringApplication.run(TaskServiceApplication.class, args);
    }

    /**
     * Seeds initial sample task data if the persistent database is empty.
     */
    @Bean
    public CommandLineRunner seedDatabase(TaskRepository repository) {
        return args -> {
            if (repository.count() == 0) {
                repository.saveAll(List.of(
                        new TaskEntity("Buy groceries", false),
                        new TaskEntity("Complete Flyrank assignment BE-02", true),
                        new TaskEntity("Review Spring Boot 4.0 release features", false)
                ));
            }
        };
    }
}
