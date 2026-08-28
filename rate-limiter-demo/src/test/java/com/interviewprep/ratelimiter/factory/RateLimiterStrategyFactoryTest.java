package com.interviewprep.ratelimiter.factory;

import com.interviewprep.ratelimiter.config.RateLimiterProperties;
import com.interviewprep.ratelimiter.model.RateLimiterType;
import com.interviewprep.ratelimiter.strategy.FixedWindowCounterStrategy;
import com.interviewprep.ratelimiter.strategy.LeakyBucketStrategy;
import com.interviewprep.ratelimiter.strategy.RateLimiterStrategy;
import com.interviewprep.ratelimiter.strategy.SlidingWindowCounterStrategy;
import com.interviewprep.ratelimiter.strategy.SlidingWindowLogStrategy;
import com.interviewprep.ratelimiter.strategy.TokenBucketStrategy;
import org.junit.jupiter.api.Test;

import java.time.Clock;
import java.time.Instant;
import java.time.ZoneOffset;
import java.util.List;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertThrows;

class RateLimiterStrategyFactoryTest {

    @Test
    void returnsActiveStrategyByConfiguredType() {
        RateLimiterProperties properties = new RateLimiterProperties();
        properties.setType(RateLimiterType.FIXED_WINDOW);
        Clock clock = Clock.fixed(Instant.parse("2026-01-01T00:00:00Z"), ZoneOffset.UTC);

        List<RateLimiterStrategy> strategies = List.of(
                new TokenBucketStrategy(properties, clock),
                new LeakyBucketStrategy(properties, clock),
                new FixedWindowCounterStrategy(properties, clock),
                new SlidingWindowLogStrategy(properties, clock),
                new SlidingWindowCounterStrategy(properties, clock));

        RateLimiterStrategyFactory factory = new RateLimiterStrategyFactory(properties, strategies);
        factory.validateActiveStrategy();

        assertEquals(RateLimiterType.FIXED_WINDOW, factory.getActiveStrategy().getType());
    }

    @Test
    void failsWhenActiveStrategyIsMissing() {
        RateLimiterProperties properties = new RateLimiterProperties();
        properties.setType(RateLimiterType.LEAKY_BUCKET);
        Clock clock = Clock.fixed(Instant.parse("2026-01-01T00:00:00Z"), ZoneOffset.UTC);

        List<RateLimiterStrategy> strategies = List.of(new TokenBucketStrategy(properties, clock));

        RateLimiterStrategyFactory factory = new RateLimiterStrategyFactory(properties, strategies);
        assertThrows(IllegalStateException.class, factory::validateActiveStrategy);
    }
}
