package com.flyrank.taskservice.controller;

import com.fasterxml.jackson.databind.ObjectMapper;
import com.flyrank.taskservice.dto.TaskCreateRequest;
import com.flyrank.taskservice.dto.TaskReplaceRequest;
import com.flyrank.taskservice.dto.TaskUpdateRequest;
import org.junit.jupiter.api.DisplayName;
import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.autoconfigure.web.servlet.AutoConfigureMockMvc;
import org.springframework.boot.test.context.SpringBootTest;
import org.springframework.http.MediaType;
import org.springframework.test.web.servlet.MockMvc;

import static org.hamcrest.Matchers.*;
import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.*;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.*;

@SpringBootTest
@AutoConfigureMockMvc
class TaskControllerTest {

    @Autowired
    private MockMvc mockMvc;

    @Autowired
    private ObjectMapper objectMapper;

    @Test
    @DisplayName("GET /tasks returns list of tasks")
    void testGetTasks() throws Exception {
        mockMvc.perform(get("/tasks"))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$", hasSize(greaterThanOrEqualTo(1))));
    }

    @Test
    @DisplayName("POST /tasks creates task using Java 21 Record Patterns")
    void testCreateTask() throws Exception {
        TaskCreateRequest request = new TaskCreateRequest("Write Integration Tests for Java 21");

        mockMvc.perform(post("/tasks")
                        .contentType(MediaType.APPLICATION_JSON)
                        .content(objectMapper.writeValueAsString(request)))
                .andExpect(status().isCreated())
                .andExpect(jsonPath("$.id", notNullValue()))
                .andExpect(jsonPath("$.title", is("Write Integration Tests for Java 21")))
                .andExpect(jsonPath("$.done", is(false)))
                .andExpect(jsonPath("$.created_at", notNullValue()));
    }

    @Test
    @DisplayName("PUT /tasks/{id} replaces existing task")
    void testReplaceTask() throws Exception {
        TaskCreateRequest create = new TaskCreateRequest("Task to Replace");
        String content = mockMvc.perform(post("/tasks")
                        .contentType(MediaType.APPLICATION_JSON)
                        .content(objectMapper.writeValueAsString(create)))
                .andReturn().getResponse().getContentAsString();
        long id = objectMapper.readTree(content).get("id").asLong();

        TaskReplaceRequest replace = new TaskReplaceRequest("Replaced Task Title Java 21", true);
        mockMvc.perform(put("/tasks/" + id)
                        .contentType(MediaType.APPLICATION_JSON)
                        .content(objectMapper.writeValueAsString(replace)))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.id", is((int) id)))
                .andExpect(jsonPath("$.title", is("Replaced Task Title Java 21")))
                .andExpect(jsonPath("$.done", is(true)));
    }

    @Test
    @DisplayName("PATCH /tasks/{id} partially updates task")
    void testPatchTask() throws Exception {
        TaskCreateRequest create = new TaskCreateRequest("Task to Patch Java 21");
        String content = mockMvc.perform(post("/tasks")
                        .contentType(MediaType.APPLICATION_JSON)
                        .content(objectMapper.writeValueAsString(create)))
                .andReturn().getResponse().getContentAsString();
        long id = objectMapper.readTree(content).get("id").asLong();

        TaskUpdateRequest patch = new TaskUpdateRequest(null, true);
        mockMvc.perform(patch("/tasks/" + id)
                        .contentType(MediaType.APPLICATION_JSON)
                        .content(objectMapper.writeValueAsString(patch)))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.id", is((int) id)))
                .andExpect(jsonPath("$.title", is("Task to Patch Java 21")))
                .andExpect(jsonPath("$.done", is(true)));
    }

    @Test
    @DisplayName("DELETE /tasks/{id} deletes task and returns 204 No Content")
    void testDeleteTask() throws Exception {
        TaskCreateRequest create = new TaskCreateRequest("Task to Delete");
        String content = mockMvc.perform(post("/tasks")
                        .contentType(MediaType.APPLICATION_JSON)
                        .content(objectMapper.writeValueAsString(create)))
                .andReturn().getResponse().getContentAsString();
        long id = objectMapper.readTree(content).get("id").asLong();

        mockMvc.perform(delete("/tasks/" + id))
                .andExpect(status().isNoContent());

        mockMvc.perform(get("/tasks/" + id))
                .andExpect(status().isNotFound());
    }

    @Test
    @DisplayName("GET /stats returns database table and task breakdown")
    void testGetStats() throws Exception {
        mockMvc.perform(get("/stats"))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.tables", hasItem("TASKS")))
                .andExpect(jsonPath("$.total_tasks", greaterThanOrEqualTo(1)));
    }
}
