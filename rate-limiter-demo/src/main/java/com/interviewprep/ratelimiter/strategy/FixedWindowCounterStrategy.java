package com.interviewprep.ratelimiter.strategy;

import com.interviewprep.ratelimiter.config.RateLimiterProperties;
import com.interviewprep.ratelimiter.model.RateLimiterDecision;
import com.interviewprep.ratelimiter.model.RateLimiterType;
import org.springframework.stereotype.Component;

import java.time.Clock;
import java.util.concurrent.ConcurrentHashMap;
import java.util.concurrent.ConcurrentMap;

@Component
public class FixedWindowCounterStrategy implements RateLimiterStrategy {

    private final RateLimiterProperties.WindowProperties config;
    private final Clock clock;
    private final ConcurrentMap<String, FixedWindowState> windows = new ConcurrentHashMap<>();

    public FixedWindowCounterStrategy(RateLimiterProperties properties, Clock clock) {
        this.config = properties.getFixedWindow();
        this.clock = clock;
    }

    @Override
    public RateLimiterDecision tryConsume(String key) {
        FixedWindowState state = windows.computeIfAbsent(key, ignored -> new FixedWindowState());
        synchronized (state) {
            resetWindowIfNeeded(state);
            long limit = config.getLimit();
            if (state.count < limit) {
                state.count++;
                return RateLimiterDecision.allowed(limit, limit - state.count);
            }
            long retryAfterSeconds = computeRetryAfterSeconds(state);
            return RateLimiterDecision.denied(limit, retryAfterSeconds);
        }
    }

    private void resetWindowIfNeeded(FixedWindowState state) {
        long nowMillis = clock.millis();
        long windowMillis = config.getWindow().toMillis();
        if (windowMillis <= 0) {
            return;
        }
        long currentWindowStart = (nowMillis / windowMillis) * windowMillis;
        if (state.windowStartMillis != currentWindowStart) {
            state.windowStartMillis = currentWindowStart;
            state.count = 0;
        }
    }

    private long computeRetryAfterSeconds(FixedWindowState state) {
        long windowMillis = config.getWindow().toMillis();
        if (windowMillis <= 0) {
            return 1;
        }
        long windowEndMillis = state.windowStartMillis + windowMillis;
        long millisRemaining = windowEndMillis - clock.millis();
        return Math.max(1, (millisRemaining + 999) / 1000);
    }

    @Override
    public RateLimiterType getType() {
        return RateLimiterType.FIXED_WINDOW;
    }

    private static final class FixedWindowState {
        private long windowStartMillis;
        private int count;

        private FixedWindowState() {
            this.windowStartMillis = -1;
        }
    }
}
