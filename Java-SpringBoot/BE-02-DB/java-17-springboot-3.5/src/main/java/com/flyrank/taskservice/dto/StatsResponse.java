package com.flyrank.taskservice.dto;

import com.fasterxml.jackson.annotation.JsonProperty;
import io.swagger.v3.oas.annotations.media.Schema;
import java.util.List;

/**
 * Payload returned by GET /stats endpoint.
 */
@Schema(description = "Database statistics payload")
public record StatsResponse(
        @Schema(description = "Database table names", example = "[\"TASKS\"]")
        List<String> tables,

        @Schema(description = "Total number of tasks", example = "5")
        @JsonProperty("total_tasks")
        long totalTasks,

        @Schema(description = "Count of completed tasks", example = "2")
        @JsonProperty("done_tasks")
        long doneTasks,

        @Schema(description = "Count of open tasks", example = "3")
        @JsonProperty("open_tasks")
        long openTasks
) {}
