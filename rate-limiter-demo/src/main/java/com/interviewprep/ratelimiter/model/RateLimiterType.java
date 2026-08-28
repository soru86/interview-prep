package com.interviewprep.ratelimiter.model;

public enum RateLimiterType {
    TOKEN_BUCKET("token-bucket"),
    LEAKY_BUCKET("leaky-bucket"),
    FIXED_WINDOW("fixed-window"),
    SLIDING_WINDOW_LOG("sliding-window-log"),
    SLIDING_WINDOW_COUNTER("sliding-window-counter");

    private final String configValue;

    RateLimiterType(String configValue) {
        this.configValue = configValue;
    }

    public String getConfigValue() {
        return configValue;
    }

    public static RateLimiterType fromConfigValue(String value) {
        for (RateLimiterType type : values()) {
            if (type.configValue.equals(value)) {
                return type;
            }
        }
        throw new IllegalArgumentException("Unknown rate limiter type: " + value);
    }
}
