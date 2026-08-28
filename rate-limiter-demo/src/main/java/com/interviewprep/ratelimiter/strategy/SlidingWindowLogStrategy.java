package com.interviewprep.ratelimiter.strategy;

import com.interviewprep.ratelimiter.config.RateLimiterProperties;
import com.interviewprep.ratelimiter.model.RateLimiterDecision;
import com.interviewprep.ratelimiter.model.RateLimiterType;
import org.springframework.stereotype.Component;

import java.time.Clock;
import java.util.ArrayDeque;
import java.util.Deque;
import java.util.concurrent.ConcurrentHashMap;
import java.util.concurrent.ConcurrentMap;

@Component
public class SlidingWindowLogStrategy implements RateLimiterStrategy {

    private final RateLimiterProperties.WindowProperties config;
    private final Clock clock;
    private final ConcurrentMap<String, Deque<Long>> requestLogs = new ConcurrentHashMap<>();

    public SlidingWindowLogStrategy(RateLimiterProperties properties, Clock clock) {
        this.config = properties.getSlidingWindowLog();
        this.clock = clock;
    }

    @Override
    public RateLimiterDecision tryConsume(String key) {
        Deque<Long> log = requestLogs.computeIfAbsent(key, ignored -> new ArrayDeque<>());
        synchronized (log) {
            pruneOldEntries(log);
            long limit = config.getLimit();
            if (log.size() < limit) {
                log.addLast(clock.millis());
                return RateLimiterDecision.allowed(limit, limit - log.size());
            }
            long retryAfterSeconds = computeRetryAfterSeconds(log);
            return RateLimiterDecision.denied(limit, retryAfterSeconds);
        }
    }

    private void pruneOldEntries(Deque<Long> log) {
        long windowMillis = config.getWindow().toMillis();
        long cutoff = clock.millis() - windowMillis;
        while (!log.isEmpty() && log.peekFirst() <= cutoff) {
            log.removeFirst();
        }
    }

    private long computeRetryAfterSeconds(Deque<Long> log) {
        if (log.isEmpty()) {
            return 1;
        }
        long windowMillis = config.getWindow().toMillis();
        long oldest = log.peekFirst();
        long millisUntilExpiry = (oldest + windowMillis) - clock.millis();
        return Math.max(1, (millisUntilExpiry + 999) / 1000);
    }

    @Override
    public RateLimiterType getType() {
        return RateLimiterType.SLIDING_WINDOW_LOG;
    }
}
