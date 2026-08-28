package com.interviewprep.ratelimiter;

import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.autoconfigure.web.servlet.AutoConfigureMockMvc;
import org.springframework.boot.test.context.SpringBootTest;
import org.springframework.http.MediaType;
import org.springframework.test.context.TestPropertySource;
import org.springframework.test.web.servlet.MockMvc;

import static org.hamcrest.Matchers.greaterThanOrEqualTo;
import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.get;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.content;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.header;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.jsonPath;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.status;

@SpringBootTest
@AutoConfigureMockMvc
@TestPropertySource(properties = {
        "rate-limiter.enabled=true",
        "rate-limiter.type=token-bucket",
        "rate-limiter.token-bucket.bucket-size=2",
        "rate-limiter.token-bucket.refill-rate=1",
        "rate-limiter.token-bucket.refill-interval=60s"
})
class RateLimiterIntegrationTest {

    @Autowired
    private MockMvc mockMvc;

    @Test
    void returnsGmtTimeWhenAllowed() throws Exception {
        mockMvc.perform(get("/api/time").header("X-Forwarded-For", "10.0.0.1"))
                .andExpect(status().isOk())
                .andExpect(content().contentTypeCompatibleWith(MediaType.APPLICATION_JSON))
                .andExpect(jsonPath("$.datetime").exists())
                .andExpect(jsonPath("$.timezone").value("GMT"))
                .andExpect(header().string("X-RateLimit-Limit", "2"))
                .andExpect(header().exists("X-RateLimit-Remaining"));
    }

    @Test
    void returns429WhenRateLimitExceeded() throws Exception {
        mockMvc.perform(get("/api/time").header("X-Forwarded-For", "10.0.0.2")).andExpect(status().isOk());
        mockMvc.perform(get("/api/time").header("X-Forwarded-For", "10.0.0.2")).andExpect(status().isOk());

        mockMvc.perform(get("/api/time").header("X-Forwarded-For", "10.0.0.2"))
                .andExpect(status().isTooManyRequests())
                .andExpect(content().contentTypeCompatibleWith(MediaType.APPLICATION_JSON))
                .andExpect(jsonPath("$.error").value("Too Many Requests"))
                .andExpect(jsonPath("$.message").value("Rate limit exceeded"))
                .andExpect(jsonPath("$.retryAfterSeconds").value(greaterThanOrEqualTo(1)))
                .andExpect(header().string("X-RateLimit-Limit", "2"))
                .andExpect(header().string("X-RateLimit-Remaining", "0"))
                .andExpect(header().exists("Retry-After"));
    }

    @Test
    void healthEndpointIsExcludedFromRateLimiting() throws Exception {
        for (int i = 0; i < 5; i++) {
            mockMvc.perform(get("/actuator/health")).andExpect(status().isOk());
        }
    }
}
