package com.flyrank.userservice.controller;

import com.fasterxml.jackson.databind.ObjectMapper;
import com.flyrank.userservice.dto.NameDto;
import com.flyrank.userservice.dto.UserCreateRequest;
import org.junit.jupiter.api.DisplayName;
import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.autoconfigure.web.servlet.AutoConfigureMockMvc;
import org.springframework.boot.test.context.SpringBootTest;
import org.springframework.http.MediaType;
import org.springframework.test.web.servlet.MockMvc;
import org.springframework.test.web.servlet.MvcResult;

import java.util.UUID;

import static org.hamcrest.Matchers.containsString;
import static org.hamcrest.Matchers.is;
import static org.hamcrest.Matchers.notNullValue;
import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.get;
import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.post;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.jsonPath;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.status;

@SpringBootTest
@AutoConfigureMockMvc
class UserControllerTest {

    @Autowired
    private MockMvc mockMvc;

    @Autowired
    private ObjectMapper objectMapper;

    @Test
    @DisplayName("POST /user with valid payload creates user and returns 201 Created")
    void testCreateUserSuccess() throws Exception {
        UserCreateRequest request = new UserCreateRequest(
                new NameDto("Jane", "Doe"),
                "jane.doe@example.com",
                "+1-555-0199"
        );

        MvcResult result = mockMvc.perform(post("/user")
                        .contentType(MediaType.APPLICATION_JSON)
                        .content(objectMapper.writeValueAsString(request)))
                .andExpect(status().isCreated())
                .andExpect(jsonPath("$.id", notNullValue()))
                .andExpect(jsonPath("$.name.first_name", is("Jane")))
                .andExpect(jsonPath("$.name.last_name", is("Doe")))
                .andExpect(jsonPath("$.email", is("jane.doe@example.com")))
                .andExpect(jsonPath("$.telephone", is("+1-555-0199")))
                .andReturn();
    }

    @Test
    @DisplayName("GET /user/{user_id} returns 200 OK for existing user")
    void testGetUserSuccess() throws Exception {
        // Create user first
        UserCreateRequest request = new UserCreateRequest(
                new NameDto("John", "Smith"),
                "john.smith@example.com",
                null
        );

        String content = mockMvc.perform(post("/user")
                        .contentType(MediaType.APPLICATION_JSON)
                        .content(objectMapper.writeValueAsString(request)))
                .andExpect(status().isCreated())
                .andReturn().getResponse().getContentAsString();

        String userIdStr = objectMapper.readTree(content).get("id").asText();

        // Retrieve user by ID
        mockMvc.perform(get("/user/" + userIdStr))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.id", is(userIdStr)))
                .andExpect(jsonPath("$.name.first_name", is("John")))
                .andExpect(jsonPath("$.name.last_name", is("Smith")));
    }

    @Test
    @DisplayName("GET /user/{user_id} returns 404 Not Found for non-existent user")
    void testGetUserNotFound() throws Exception {
        UUID randomId = UUID.randomUUID();

        mockMvc.perform(get("/user/" + randomId))
                .andExpect(status().isNotFound())
                .andExpect(jsonPath("$.detail", containsString("User with id '" + randomId + "' not found")));
    }

    @Test
    @DisplayName("POST /user with missing name object returns 422 Unprocessable Entity")
    void testCreateUserMissingName() throws Exception {
        String invalidJson = """
                {
                    "email": "test@example.com"
                }
                """;

        mockMvc.perform(post("/user")
                        .contentType(MediaType.APPLICATION_JSON)
                        .content(invalidJson))
                .andExpect(status().isUnprocessableEntity())
                .andExpect(jsonPath("$.detail", containsString("name: name object is required")));
    }

    @Test
    @DisplayName("POST /user with missing first_name returns 422 Unprocessable Entity")
    void testCreateUserMissingFirstName() throws Exception {
        String invalidJson = """
                {
                    "name": {
                        "last_name": "Doe"
                    }
                }
                """;

        mockMvc.perform(post("/user")
                        .contentType(MediaType.APPLICATION_JSON)
                        .content(invalidJson))
                .andExpect(status().isUnprocessableEntity())
                .andExpect(jsonPath("$.detail", containsString("first_name")));
    }

    @Test
    @DisplayName("POST /user with invalid email format returns 422 Unprocessable Entity")
    void testCreateUserInvalidEmail() throws Exception {
        String invalidJson = """
                {
                    "name": {
                        "first_name": "Jane",
                        "last_name": "Doe"
                    },
                    "email": "not-an-email"
                }
                """;

        mockMvc.perform(post("/user")
                        .contentType(MediaType.APPLICATION_JSON)
                        .content(invalidJson))
                .andExpect(status().isUnprocessableEntity())
                .andExpect(jsonPath("$.detail", containsString("email: value is not a valid email address")));
    }

    @Test
    @DisplayName("POST /user with unrecognized unknown field returns 422 Unprocessable Entity")
    void testCreateUserForbiddenExtraField() throws Exception {
        String jsonWithExtraField = """
                {
                    "name": {
                        "first_name": "Jane",
                        "last_name": "Doe"
                    },
                    "unknown_field": "disallowed"
                }
                """;

        mockMvc.perform(post("/user")
                        .contentType(MediaType.APPLICATION_JSON)
                        .content(jsonWithExtraField))
                .andExpect(status().isUnprocessableEntity())
                .andExpect(jsonPath("$.detail", containsString("forbidden field")));
    }
}
