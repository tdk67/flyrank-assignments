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

import java.util.UUID;

import static org.hamcrest.Matchers.*;
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
    @DisplayName("POST /user with valid payload creates user using Java 21 Record Patterns")
    void testCreateUserSuccess() throws Exception {
        UserCreateRequest request = new UserCreateRequest(
                new NameDto("Jane", "Doe"),
                "jane.doe@example.com",
                "+1-555-0199"
        );

        mockMvc.perform(post("/user")
                        .contentType(MediaType.APPLICATION_JSON)
                        .content(objectMapper.writeValueAsString(request)))
                .andExpect(status().isCreated())
                .andExpect(jsonPath("$.id", notNullValue()))
                .andExpect(jsonPath("$.name.first_name", is("Jane")))
                .andExpect(jsonPath("$.name.last_name", is("Doe")))
                .andExpect(jsonPath("$.email", is("jane.doe@example.com")))
                .andExpect(jsonPath("$.telephone", is("+1-555-0199")));
    }

    @Test
    @DisplayName("GET /user/{user_id} returns 200 OK for existing user")
    void testGetUserSuccess() throws Exception {
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

        mockMvc.perform(get("/user/" + userIdStr))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.id", is(userIdStr)))
                .andExpect(jsonPath("$.name.first_name", is("John")))
                .andExpect(jsonPath("$.name.last_name", is("Smith")));
    }

    @Test
    @DisplayName("GET /user/{user_id} returns 404 Not Found for missing user")
    void testGetUserNotFound() throws Exception {
        UUID randomId = UUID.randomUUID();

        mockMvc.perform(get("/user/" + randomId))
                .andExpect(status().isNotFound())
                .andExpect(jsonPath("$.detail", containsString("User with id '" + randomId + "' not found")));
    }

    @Test
    @DisplayName("POST /user with unrecognized extra field returns 422 Unprocessable Entity")
    void testCreateUserForbiddenExtraField() throws Exception {
        String jsonWithExtraField = """
                {
                    "name": {
                        "first_name": "Jane",
                        "last_name": "Doe"
                    },
                    "forbidden_extra": "disallowed"
                }
                """;

        mockMvc.perform(post("/user")
                        .contentType(MediaType.APPLICATION_JSON)
                        .content(jsonWithExtraField))
                .andExpect(status().isUnprocessableEntity())
                .andExpect(jsonPath("$.detail", containsString("forbidden field")));
    }
}
