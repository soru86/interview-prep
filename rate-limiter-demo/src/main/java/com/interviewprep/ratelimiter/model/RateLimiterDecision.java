package com.interviewprep.ratelimiter.model;

public record RateLimiterDecision(
        boolean allowed,
        long limit,
        long remaining,
        long retryAfterSeconds
) {
    public static RateLimiterDecision allowed(long limit, long remaining) {
        return new RateLimiterDecision(true, limit, remaining, 0);
    }

    public static RateLimiterDecision denied(long limit, long retryAfterSeconds) {
        return new RateLimiterDecision(false, limit, 0, retryAfterSeconds);
    }
}
