package com.interviewprep.ratelimiter.strategy;

import com.interviewprep.ratelimiter.config.RateLimiterProperties;
import org.junit.jupiter.api.Test;

import java.time.Clock;
import java.time.Duration;
import java.time.Instant;
import java.time.ZoneOffset;

import static com.interviewprep.ratelimiter.strategy.StrategyTestSupport.assertAllowed;
import static com.interviewprep.ratelimiter.strategy.StrategyTestSupport.assertDenied;
import static com.interviewprep.ratelimiter.strategy.StrategyTestSupport.fixedClock;
import static com.interviewprep.ratelimiter.strategy.StrategyTestSupport.properties;

class SlidingWindowLogStrategyTest {

    @Test
    void allowsRequestsUpToLimitWithinWindow() {
        RateLimiterProperties props = properties();
        props.getSlidingWindowLog().setLimit(2);
        props.getSlidingWindowLog().setWindow(Duration.ofSeconds(10));

        Clock clock = fixedClock(Instant.parse("2026-01-01T00:00:00Z"));
        SlidingWindowLogStrategy strategy = new SlidingWindowLogStrategy(props, clock);

        assertAllowed(strategy.tryConsume("client-1"), 2, 1);
        assertAllowed(strategy.tryConsume("client-1"), 2, 0);
        assertDenied(strategy.tryConsume("client-1"), 2);
    }

    @Test
    void prunesExpiredTimestamps() {
        RateLimiterProperties props = properties();
        props.getSlidingWindowLog().setLimit(1);
        props.getSlidingWindowLog().setWindow(Duration.ofSeconds(5));

        MutableClock clock = new MutableClock(Instant.parse("2026-01-01T00:00:00Z"), ZoneOffset.UTC);
        SlidingWindowLogStrategy strategy = new SlidingWindowLogStrategy(props, clock);

        assertAllowed(strategy.tryConsume("client-1"), 1, 0);
        assertDenied(strategy.tryConsume("client-1"), 1);

        clock.advance(Duration.ofSeconds(6));
        assertAllowed(strategy.tryConsume("client-1"), 1, 0);
    }
}
