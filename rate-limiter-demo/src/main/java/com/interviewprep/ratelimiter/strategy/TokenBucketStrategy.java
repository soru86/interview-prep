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
public class TokenBucketStrategy implements RateLimiterStrategy {

    private final RateLimiterProperties.TokenBucketProperties config;
    private final Clock clock;
    private final ConcurrentMap<String, TokenBucketState> buckets = new ConcurrentHashMap<>();

    public TokenBucketStrategy(RateLimiterProperties properties, Clock clock) {
        this.config = properties.getTokenBucket();
        this.clock = clock;
    }

    @Override
    public RateLimiterDecision tryConsume(String key) {
        TokenBucketState state = buckets.computeIfAbsent(
                key, ignored -> new TokenBucketState(config.getBucketSize(), clock.millis()));
        synchronized (state) {
            refill(state);
            long limit = config.getBucketSize();
            if (state.tokens >= 1) {
                state.tokens--;
                return RateLimiterDecision.allowed(limit, (long) state.tokens);
            }
            long retryAfterSeconds = computeRetryAfterSeconds(state);
            return RateLimiterDecision.denied(limit, retryAfterSeconds);
        }
    }

    private void refill(TokenBucketState state) {
        long nowMillis = clock.millis();
        Duration refillInterval = config.getRefillInterval();
        long intervalMillis = refillInterval.toMillis();
        if (intervalMillis <= 0) {
            return;
        }

        long elapsedIntervals = (nowMillis - state.lastRefillMillis) / intervalMillis;
        if (elapsedIntervals <= 0) {
            return;
        }

        long tokensToAdd = elapsedIntervals * config.getRefillRate();
        state.tokens = Math.min(config.getBucketSize(), state.tokens + tokensToAdd);
        state.lastRefillMillis += elapsedIntervals * intervalMillis;
    }

    private long computeRetryAfterSeconds(TokenBucketState state) {
        Duration refillInterval = config.getRefillInterval();
        long intervalMillis = refillInterval.toMillis();
        if (intervalMillis <= 0) {
            return 1;
        }
        long elapsedSinceLastRefill = clock.millis() - state.lastRefillMillis;
        long millisUntilNextRefill = intervalMillis - (elapsedSinceLastRefill % intervalMillis);
        return Math.max(1, (millisUntilNextRefill + 999) / 1000);
    }

    @Override
    public RateLimiterType getType() {
        return RateLimiterType.TOKEN_BUCKET;
    }

    private static final class TokenBucketState {
        private double tokens;
        private long lastRefillMillis;

        private TokenBucketState(int bucketSize, long nowMillis) {
            this.tokens = bucketSize;
            this.lastRefillMillis = nowMillis;
        }
    }
}
