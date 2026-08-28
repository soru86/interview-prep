package com.interviewprep.ratelimiter.strategy;

import com.interviewprep.ratelimiter.config.RateLimiterProperties;
import org.junit.jupiter.api.Test;

import java.time.Clock;
import java.time.Duration;
import java.time.Instant;

import static com.interviewprep.ratelimiter.strategy.StrategyTestSupport.assertAllowed;
import static com.interviewprep.ratelimiter.strategy.StrategyTestSupport.assertDenied;
import static com.interviewprep.ratelimiter.strategy.StrategyTestSupport.fixedClock;
import static com.interviewprep.ratelimiter.strategy.StrategyTestSupport.properties;

class SlidingWindowCounterStrategyTest {

    @Test
    void allowsRequestsUpToLimit() {
        RateLimiterProperties props = properties();
        props.getSlidingWindowCounter().setLimit(2);
        props.getSlidingWindowCounter().setWindow(Duration.ofSeconds(10));
        props.getSlidingWindowCounter().setSubWindows(2);

        Clock clock = fixedClock(Instant.parse("2026-01-01T00:00:00Z"));
        SlidingWindowCounterStrategy strategy = new SlidingWindowCounterStrategy(props, clock);

        assertAllowed(strategy.tryConsume("client-1"), 2, 1);
        assertAllowed(strategy.tryConsume("client-1"), 2, 0);
        assertDenied(strategy.tryConsume("client-1"), 2);
    }

    @Test
    void isolatesKeys() {
        RateLimiterProperties props = properties();
        props.getSlidingWindowCounter().setLimit(1);
        props.getSlidingWindowCounter().setWindow(Duration.ofSeconds(10));
        props.getSlidingWindowCounter().setSubWindows(2);

        Clock clock = fixedClock(Instant.parse("2026-01-01T00:00:00Z"));
        SlidingWindowCounterStrategy strategy = new SlidingWindowCounterStrategy(props, clock);

        assertAllowed(strategy.tryConsume("client-a"), 1, 0);
        assertAllowed(strategy.tryConsume("client-b"), 1, 0);
    }
}
