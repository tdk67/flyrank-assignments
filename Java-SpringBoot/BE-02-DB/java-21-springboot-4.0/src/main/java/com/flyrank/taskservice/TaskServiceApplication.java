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

    @Bean
    public CommandLineRunner seedDatabase(TaskRepository repository) {
        return args -> {
            if (repository.count() == 0) {
                repository.saveAll(List.of(
                        new TaskEntity("Buy groceries", false),
                        new TaskEntity("Complete Flyrank assignment BE-02 in Java 21", true),
                        new TaskEntity("Explore Virtual Threads & Sequenced Collections", false)
                ));
            }
        };
    }
}
