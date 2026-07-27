package com.flyrank.taskservice.controller

import com.fasterxml.jackson.databind.ObjectMapper
import com.flyrank.taskservice.dto.TaskCreateRequest
import com.flyrank.taskservice.dto.TaskReplaceRequest
import com.flyrank.taskservice.dto.TaskUpdateRequest
import org.hamcrest.Matchers.*
import org.junit.jupiter.api.DisplayName
import org.junit.jupiter.api.Test
import org.springframework.beans.factory.annotation.Autowired
import org.springframework.boot.test.autoconfigure.web.servlet.AutoConfigureMockMvc
import org.springframework.boot.test.context.SpringBootTest
import org.springframework.http.MediaType
import org.springframework.test.web.servlet.MockMvc
import org.springframework.test.web.servlet.request.MockMvcRequestBuilders.*
import org.springframework.test.web.servlet.result.MockMvcResultMatchers.*

@SpringBootTest
@AutoConfigureMockMvc
class TaskControllerTest {

    @Autowired
    private lateinit var mockMvc: MockMvc

    @Autowired
    private lateinit var objectMapper: ObjectMapper

    @Test
    @DisplayName("GET /tasks returns list of tasks")
    fun testGetTasks() {
        mockMvc.perform(get("/tasks"))
            .andExpect(status().isOk)
            .andExpect(jsonPath("$", hasSize<Any>(greaterThanOrEqualTo(1))))
    }

    @Test
    @DisplayName("POST /tasks creates task in Kotlin")
    fun testCreateTask() {
        val request = TaskCreateRequest("Write Kotlin Integration Tests")

        mockMvc.perform(
            post("/tasks")
                .contentType(MediaType.APPLICATION_JSON)
                .content(objectMapper.writeValueAsString(request))
        )
            .andExpect(status().isCreated)
            .andExpect(jsonPath("$.id", notNullValue()))
            .andExpect(jsonPath("$.title", `is`("Write Kotlin Integration Tests")))
            .andExpect(jsonPath("$.done", `is`(false)))
            .andExpect(jsonPath("$.created_at", notNullValue()))
    }

    @Test
    @DisplayName("PUT /tasks/{id} replaces existing task")
    fun testReplaceTask() {
        val create = TaskCreateRequest("Task to Replace Kotlin")
        val content = mockMvc.perform(
            post("/tasks")
                .contentType(MediaType.APPLICATION_JSON)
                .content(objectMapper.writeValueAsString(create))
        ).andReturn().response.contentAsString
        val id = objectMapper.readTree(content).get("id").asLong()

        val replace = TaskReplaceRequest("Replaced Task Title Kotlin", true)
        mockMvc.perform(
            put("/tasks/$id")
                .contentType(MediaType.APPLICATION_JSON)
                .content(objectMapper.writeValueAsString(replace))
        )
            .andExpect(status().isOk)
            .andExpect(jsonPath("$.id", `is`(id.toInt())))
            .andExpect(jsonPath("$.title", `is`("Replaced Task Title Kotlin")))
            .andExpect(jsonPath("$.done", `is`(true)))
    }

    @Test
    @DisplayName("PATCH /tasks/{id} partially updates task")
    fun testPatchTask() {
        val create = TaskCreateRequest("Task to Patch Kotlin")
        val content = mockMvc.perform(
            post("/tasks")
                .contentType(MediaType.APPLICATION_JSON)
                .content(objectMapper.writeValueAsString(create))
        ).andReturn().response.contentAsString
        val id = objectMapper.readTree(content).get("id").asLong()

        val patch = TaskUpdateRequest(null, true)
        mockMvc.perform(
            patch("/tasks/$id")
                .contentType(MediaType.APPLICATION_JSON)
                .content(objectMapper.writeValueAsString(patch))
        )
            .andExpect(status().isOk)
            .andExpect(jsonPath("$.id", `is`(id.toInt())))
            .andExpect(jsonPath("$.title", `is`("Task to Patch Kotlin")))
            .andExpect(jsonPath("$.done", `is`(true)))
    }

    @Test
    @DisplayName("DELETE /tasks/{id} deletes task and returns 204 No Content")
    fun testDeleteTask() {
        val create = TaskCreateRequest("Task to Delete Kotlin")
        val content = mockMvc.perform(
            post("/tasks")
                .contentType(MediaType.APPLICATION_JSON)
                .content(objectMapper.writeValueAsString(create))
        ).andReturn().response.contentAsString
        val id = objectMapper.readTree(content).get("id").asLong()

        mockMvc.perform(delete("/tasks/$id"))
            .andExpect(status().isNoContent)

        mockMvc.perform(get("/tasks/$id"))
            .andExpect(status().isNotFound)
    }

    @Test
    @DisplayName("GET /stats returns database table and task breakdown")
    fun testGetStats() {
        mockMvc.perform(get("/stats"))
            .andExpect(status().isOk)
            .andExpect(jsonPath("$.tables", hasItem("TASKS")))
            .andExpect(jsonPath("$.total_tasks", greaterThanOrEqualTo(1)))
    }
}
