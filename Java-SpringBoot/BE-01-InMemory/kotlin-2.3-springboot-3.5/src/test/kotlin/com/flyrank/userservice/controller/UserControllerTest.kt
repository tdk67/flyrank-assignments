package com.flyrank.userservice.controller

import com.fasterxml.jackson.databind.ObjectMapper
import com.flyrank.userservice.dto.NameDto
import com.flyrank.userservice.dto.UserCreateRequest
import org.hamcrest.Matchers.*
import org.junit.jupiter.api.DisplayName
import org.junit.jupiter.api.Test
import org.springframework.beans.factory.annotation.Autowired
import org.springframework.boot.test.autoconfigure.web.servlet.AutoConfigureMockMvc
import org.springframework.boot.test.context.SpringBootTest
import org.springframework.http.MediaType
import org.springframework.test.web.servlet.MockMvc
import org.springframework.test.web.servlet.request.MockMvcRequestBuilders.get
import org.springframework.test.web.servlet.request.MockMvcRequestBuilders.post
import org.springframework.test.web.servlet.result.MockMvcResultMatchers.jsonPath
import org.springframework.test.web.servlet.result.MockMvcResultMatchers.status
import java.util.UUID

@SpringBootTest
@AutoConfigureMockMvc
class UserControllerTest {

    @Autowired
    private lateinit var mockMvc: MockMvc

    @Autowired
    private lateinit var objectMapper: ObjectMapper

    @Test
    @DisplayName("POST /user with valid payload creates user in Kotlin")
    fun testCreateUserSuccess() {
        val request = UserCreateRequest(
            name = NameDto("Jane", "Doe"),
            email = "jane.doe@example.com",
            telephone = "+1-555-0199"
        )

        mockMvc.perform(
            post("/user")
                .contentType(MediaType.APPLICATION_JSON)
                .content(objectMapper.writeValueAsString(request))
        )
            .andExpect(status().isCreated)
            .andExpect(jsonPath("$.id", notNullValue()))
            .andExpect(jsonPath("$.name.first_name", `is`("Jane")))
            .andExpect(jsonPath("$.name.last_name", `is`("Doe")))
            .andExpect(jsonPath("$.email", `is`("jane.doe@example.com")))
            .andExpect(jsonPath("$.telephone", `is`("+1-555-0199")))
    }

    @Test
    @DisplayName("GET /user/{user_id} returns 200 OK for existing user")
    fun testGetUserSuccess() {
        val request = UserCreateRequest(
            name = NameDto("John", "Smith"),
            email = "john.smith@example.com"
        )

        val content = mockMvc.perform(
            post("/user")
                .contentType(MediaType.APPLICATION_JSON)
                .content(objectMapper.writeValueAsString(request))
        )
            .andExpect(status().isCreated)
            .andReturn().response.contentAsString

        val userIdStr = objectMapper.readTree(content).get("id").asText()

        mockMvc.perform(get("/user/$userIdStr"))
            .andExpect(status().isOk)
            .andExpect(jsonPath("$.id", `is`(userIdStr)))
            .andExpect(jsonPath("$.name.first_name", `is`("John")))
            .andExpect(jsonPath("$.name.last_name", `is`("Smith")))
    }

    @Test
    @DisplayName("GET /user/{user_id} returns 404 Not Found for missing user")
    fun testGetUserNotFound() {
        val randomId = UUID.randomUUID()

        mockMvc.perform(get("/user/$randomId"))
            .andExpect(status().isNotFound)
            .andExpect(jsonPath("$.detail", containsString("User with id '$randomId' not found")))
    }

    @Test
    @DisplayName("POST /user with unrecognized extra field returns 422 Unprocessable Entity")
    fun testCreateUserForbiddenExtraField() {
        val jsonWithExtraField = """
            {
                "name": {
                    "first_name": "Jane",
                    "last_name": "Doe"
                },
                "forbidden_extra": "disallowed"
            }
        """.trimIndent()

        mockMvc.perform(
            post("/user")
                .contentType(MediaType.APPLICATION_JSON)
                .content(jsonWithExtraField)
        )
            .andExpect(status().isUnprocessableEntity)
            .andExpect(jsonPath("$.detail", containsString("forbidden field")))
    }
}
