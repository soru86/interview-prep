package com.interviewprep.ratelimiter.controller;

import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

import java.time.Instant;
import java.util.Map;

@RestController
@RequestMapping("/api")
public class TimeController {

    @GetMapping("/time")
    public Map<String, String> currentTimeGmt() {
        return Map.of(
                "datetime", Instant.now().toString(),
                "timezone", "GMT"
        );
    }
}
