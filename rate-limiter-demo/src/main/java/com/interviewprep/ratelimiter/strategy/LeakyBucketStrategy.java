package com.interviewprep.ratelimiter.strategy;

import com.interviewprep.ratelimiter.config.RateLimiterProperties;
import com.interviewprep.ratelimiter.model.RateLimiterDecision;
import com.interviewprep.ratelimiter.model.RateLimiterType;
import org.springframework.stereotype.Component;

import java.time.Clock;
import java.time.Duration;
import java.util.concurrent.ConcurrentHashMap;
import java.util.concurrent.ConcurrentMap;

@Component
public class LeakyBucketStrategy implements RateLimiterStrategy {

    private final RateLimiterProperties.LeakyBucketProperties config;
    private final Clock clock;
    private final ConcurrentMap<String, LeakyBucketState> buckets = new ConcurrentHashMap<>();

    public LeakyBucketStrategy(RateLimiterProperties properties, Clock clock) {
        this.config = properties.getLeakyBucket();
        this.clock = clock;
    }

    @Override
    public RateLimiterDecision tryConsume(String key) {
        LeakyBucketState state = buckets.computeIfAbsent(key, ignored -> new LeakyBucketState(clock.millis()));
        synchronized (state) {
            leak(state);
            long limit = config.getBucketSize();
            if (state.queueSize < config.getBucketSize()) {
                state.queueSize++;
                long remaining = config.getBucketSize() - state.queueSize;
                return RateLimiterDecision.allowed(limit, remaining);
            }
            long retryAfterSeconds = computeRetryAfterSeconds(state);
            return RateLimiterDecision.denied(limit, retryAfterSeconds);
        }
    }

    private void leak(LeakyBucketState state) {
        long nowMillis = clock.millis();
        Duration leakInterval = config.getLeakInterval();
        long intervalMillis = leakInterval.toMillis();
        if (intervalMillis <= 0) {
            return;
        }

        long elapsedIntervals = (nowMillis - state.lastLeakMillis) / intervalMillis;
        if (elapsedIntervals <= 0) {
            return;
        }

        long leaked = elapsedIntervals * config.getLeakRate();
        state.queueSize = (int) Math.max(0, state.queueSize - leaked);
        state.lastLeakMillis += elapsedIntervals * intervalMillis;
    }

    private long computeRetryAfterSeconds(LeakyBucketState state) {
        Duration leakInterval = config.getLeakInterval();
        long intervalMillis = leakInterval.toMillis();
        if (intervalMillis <= 0) {
            return 1;
        }
        long elapsedSinceLastLeak = clock.millis() - state.lastLeakMillis;
        long millisUntilNextLeak = intervalMillis - (elapsedSinceLastLeak % intervalMillis);
        return Math.max(1, (millisUntilNextLeak + 999) / 1000);
    }

    @Override
    public RateLimiterType getType() {
        return RateLimiterType.LEAKY_BUCKET;
    }

    private static final class LeakyBucketState {
        private int queueSize;
        private long lastLeakMillis;

        private LeakyBucketState(long nowMillis) {
            this.lastLeakMillis = nowMillis;
        }
    }
}
