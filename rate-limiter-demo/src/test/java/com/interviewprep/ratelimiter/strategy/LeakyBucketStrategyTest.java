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

class LeakyBucketStrategyTest {

    @Test
    void allowsRequestsUpToBucketSize() {
        RateLimiterProperties props = properties();
        props.getLeakyBucket().setBucketSize(2);
        props.getLeakyBucket().setLeakRate(1);
        props.getLeakyBucket().setLeakInterval(Duration.ofSeconds(1));

        Clock clock = fixedClock(Instant.parse("2026-01-01T00:00:00Z"));
        LeakyBucketStrategy strategy = new LeakyBucketStrategy(props, clock);

        assertAllowed(strategy.tryConsume("client-1"), 2, 1);
        assertAllowed(strategy.tryConsume("client-1"), 2, 0);
        assertDenied(strategy.tryConsume("client-1"), 2);
    }

    @Test
    void leaksRequestsAfterInterval() {
        RateLimiterProperties props = properties();
        props.getLeakyBucket().setBucketSize(2);
        props.getLeakyBucket().setLeakRate(2);
        props.getLeakyBucket().setLeakInterval(Duration.ofSeconds(1));

        MutableClock clock = new MutableClock(Instant.parse("2026-01-01T00:00:00Z"), ZoneOffset.UTC);
        LeakyBucketStrategy strategy = new LeakyBucketStrategy(props, clock);

        assertAllowed(strategy.tryConsume("client-1"), 2, 1);
        assertAllowed(strategy.tryConsume("client-1"), 2, 0);
        assertDenied(strategy.tryConsume("client-1"), 2);

        clock.advance(Duration.ofSeconds(1));
        assertAllowed(strategy.tryConsume("client-1"), 2, 1);
    }
}
