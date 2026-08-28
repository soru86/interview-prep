package com.interviewprep.ratelimiter.strategy;

import com.interviewprep.ratelimiter.config.RateLimiterProperties;
import com.interviewprep.ratelimiter.model.RateLimiterDecision;
import org.junit.jupiter.api.Test;

import java.time.Clock;
import java.time.Duration;
import java.time.Instant;
import java.time.ZoneOffset;

import static com.interviewprep.ratelimiter.strategy.StrategyTestSupport.assertAllowed;
import static com.interviewprep.ratelimiter.strategy.StrategyTestSupport.assertDenied;
import static com.interviewprep.ratelimiter.strategy.StrategyTestSupport.fixedClock;
import static com.interviewprep.ratelimiter.strategy.StrategyTestSupport.properties;
import static org.junit.jupiter.api.Assertions.assertTrue;

class TokenBucketStrategyTest {

    @Test
    void allowsRequestsUpToBucketSize() {
        RateLimiterProperties props = properties();
        props.getTokenBucket().setBucketSize(3);
        props.getTokenBucket().setRefillRate(1);
        props.getTokenBucket().setRefillInterval(Duration.ofSeconds(1));

        Clock clock = fixedClock(Instant.parse("2026-01-01T00:00:00Z"));
        TokenBucketStrategy strategy = new TokenBucketStrategy(props, clock);

        assertAllowed(strategy.tryConsume("client-1"), 3, 2);
        assertAllowed(strategy.tryConsume("client-1"), 3, 1);
        assertAllowed(strategy.tryConsume("client-1"), 3, 0);
        assertDenied(strategy.tryConsume("client-1"), 3);
    }

    @Test
    void refillsTokensAfterInterval() {
        RateLimiterProperties props = properties();
        props.getTokenBucket().setBucketSize(2);
        props.getTokenBucket().setRefillRate(2);
        props.getTokenBucket().setRefillInterval(Duration.ofSeconds(1));

        MutableClock clock = new MutableClock(Instant.parse("2026-01-01T00:00:00Z"), ZoneOffset.UTC);
        TokenBucketStrategy strategy = new TokenBucketStrategy(props, clock);

        assertAllowed(strategy.tryConsume("client-1"), 2, 1);
        assertAllowed(strategy.tryConsume("client-1"), 2, 0);
        assertDenied(strategy.tryConsume("client-1"), 2);

        clock.advance(Duration.ofSeconds(1));
        assertAllowed(strategy.tryConsume("client-1"), 2, 1);
    }

    @Test
    void isolatesKeys() {
        RateLimiterProperties props = properties();
        props.getTokenBucket().setBucketSize(1);
        props.getTokenBucket().setRefillRate(1);
        props.getTokenBucket().setRefillInterval(Duration.ofSeconds(1));

        Clock clock = fixedClock(Instant.parse("2026-01-01T00:00:00Z"));
        TokenBucketStrategy strategy = new TokenBucketStrategy(props, clock);

        assertAllowed(strategy.tryConsume("client-a"), 1, 0);
        assertAllowed(strategy.tryConsume("client-b"), 1, 0);
        assertDenied(strategy.tryConsume("client-a"), 1);
    }

    @Test
    void deniedDecisionIncludesRetryAfter() {
        RateLimiterProperties props = properties();
        props.getTokenBucket().setBucketSize(1);
        props.getTokenBucket().setRefillRate(1);
        props.getTokenBucket().setRefillInterval(Duration.ofSeconds(5));

        Clock clock = fixedClock(Instant.parse("2026-01-01T00:00:00Z"));
        TokenBucketStrategy strategy = new TokenBucketStrategy(props, clock);

        strategy.tryConsume("client-1");
        RateLimiterDecision denied = strategy.tryConsume("client-1");
        assertDenied(denied, 1);
        assertTrue(denied.retryAfterSeconds() >= 1);
    }
}
