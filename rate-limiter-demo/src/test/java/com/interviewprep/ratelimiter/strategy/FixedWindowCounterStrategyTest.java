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

class FixedWindowCounterStrategyTest {

    @Test
    void allowsRequestsUpToLimitWithinWindow() {
        RateLimiterProperties props = properties();
        props.getFixedWindow().setLimit(2);
        props.getFixedWindow().setWindow(Duration.ofSeconds(10));

        Clock clock = fixedClock(Instant.parse("2026-01-01T00:00:00Z"));
        FixedWindowCounterStrategy strategy = new FixedWindowCounterStrategy(props, clock);

        assertAllowed(strategy.tryConsume("client-1"), 2, 1);
        assertAllowed(strategy.tryConsume("client-1"), 2, 0);
        assertDenied(strategy.tryConsume("client-1"), 2);
    }

    @Test
    void resetsCounterAtWindowBoundary() {
        RateLimiterProperties props = properties();
        props.getFixedWindow().setLimit(1);
        props.getFixedWindow().setWindow(Duration.ofSeconds(10));

        MutableClock clock = new MutableClock(Instant.parse("2026-01-01T00:00:00Z"), ZoneOffset.UTC);
        FixedWindowCounterStrategy strategy = new FixedWindowCounterStrategy(props, clock);

        assertAllowed(strategy.tryConsume("client-1"), 1, 0);
        assertDenied(strategy.tryConsume("client-1"), 1);

        clock.advance(Duration.ofSeconds(10));
        assertAllowed(strategy.tryConsume("client-1"), 1, 0);
    }
}
