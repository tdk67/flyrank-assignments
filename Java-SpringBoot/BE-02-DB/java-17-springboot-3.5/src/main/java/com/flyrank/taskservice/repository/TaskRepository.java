package com.flyrank.taskservice.repository;

import com.flyrank.taskservice.entity.TaskEntity;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.Query;
import org.springframework.data.repository.query.Param;
import org.springframework.stereotype.Repository;

import java.util.List;

/**
 * Spring Data JPA Repository for TaskEntity.
 */
@Repository
public interface TaskRepository extends JpaRepository<TaskEntity, Long> {

    @Query("SELECT t FROM TaskEntity t WHERE " +
           "(:search IS NULL OR LOWER(t.title) LIKE LOWER(CONCAT('%', :search, '%'))) AND " +
           "(:done IS NULL OR t.done = :done) " +
           "ORDER BY t.id ASC")
    List<TaskEntity> filterTasks(@Param("search") String search, @Param("done") Boolean done);

    long countByDone(boolean done);
}
