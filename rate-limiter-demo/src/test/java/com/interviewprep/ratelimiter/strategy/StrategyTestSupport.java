package com.interviewprep.ratelimiter.strategy;

import com.interviewprep.ratelimiter.config.RateLimiterProperties;
import com.interviewprep.ratelimiter.model.RateLimiterDecision;

import java.time.Clock;
import java.time.Duration;
import java.time.Instant;
import java.time.ZoneOffset;

final class StrategyTestSupport {

    private StrategyTestSupport() {
    }

    static Clock fixedClock(Instant instant) {
        return Clock.fixed(instant, ZoneOffset.UTC);
    }

    static Clock offsetClock(Clock base, Duration offset) {
        return Clock.offset(base, offset);
    }

    static RateLimiterProperties properties() {
        return new RateLimiterProperties();
    }

    static void assertAllowed(RateLimiterDecision decision, long expectedLimit, long expectedRemaining) {
        if (!decision.allowed()) {
            throw new AssertionError("Expected allowed decision");
        }
        if (decision.limit() != expectedLimit || decision.remaining() != expectedRemaining) {
            throw new AssertionError(
                    "Expected limit=" + expectedLimit + ", remaining=" + expectedRemaining
                            + " but got limit=" + decision.limit() + ", remaining=" + decision.remaining());
        }
    }

    static void assertDenied(RateLimiterDecision decision, long expectedLimit) {
        if (decision.allowed()) {
            throw new AssertionError("Expected denied decision");
        }
        if (decision.limit() != expectedLimit || decision.remaining() != 0) {
            throw new AssertionError(
                    "Expected denied with limit=" + expectedLimit
                            + " but got limit=" + decision.limit() + ", remaining=" + decision.remaining());
        }
        if (decision.retryAfterSeconds() <= 0) {
            throw new AssertionError("Expected positive retryAfterSeconds");
        }
    }
}
