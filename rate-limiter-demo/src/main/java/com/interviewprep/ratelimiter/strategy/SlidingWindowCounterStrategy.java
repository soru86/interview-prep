package com.interviewprep.ratelimiter.strategy;

import com.interviewprep.ratelimiter.config.RateLimiterProperties;
import com.interviewprep.ratelimiter.model.RateLimiterDecision;
import com.interviewprep.ratelimiter.model.RateLimiterType;
import org.springframework.stereotype.Component;

import java.time.Clock;
import java.util.concurrent.ConcurrentHashMap;
import java.util.concurrent.ConcurrentMap;

@Component
public class SlidingWindowCounterStrategy implements RateLimiterStrategy {

    private final RateLimiterProperties.SlidingWindowCounterProperties config;
    private final Clock clock;
    private final ConcurrentMap<String, SlidingWindowCounterState> counters = new ConcurrentHashMap<>();

    public SlidingWindowCounterStrategy(RateLimiterProperties properties, Clock clock) {
        this.config = properties.getSlidingWindowCounter();
        this.clock = clock;
    }

    @Override
    public RateLimiterDecision tryConsume(String key) {
        SlidingWindowCounterState state = counters.computeIfAbsent(key, ignored -> new SlidingWindowCounterState(config.getSubWindows()));
        synchronized (state) {
            advanceWindow(state);
            double weightedCount = computeWeightedCount(state);
            long limit = config.getLimit();
            if (weightedCount < limit) {
                state.currentCounts[state.currentSubWindowIndex]++;
                double newWeightedCount = computeWeightedCount(state);
                long remaining = Math.max(0, limit - (long) Math.ceil(newWeightedCount));
                return RateLimiterDecision.allowed(limit, remaining);
            }
            long retryAfterSeconds = computeRetryAfterSeconds(state);
            return RateLimiterDecision.denied(limit, retryAfterSeconds);
        }
    }

    private void advanceWindow(SlidingWindowCounterState state) {
        long windowMillis = config.getWindow().toMillis();
        int subWindows = config.getSubWindows();
        long subWindowMillis = windowMillis / subWindows;
        if (subWindowMillis <= 0) {
            return;
        }

        long nowMillis = clock.millis();
        long currentWindowStart = (nowMillis / windowMillis) * windowMillis;
        int currentSubWindowIndex = (int) ((nowMillis - currentWindowStart) / subWindowMillis);
        currentSubWindowIndex = Math.min(currentSubWindowIndex, subWindows - 1);

        if (state.windowStartMillis != currentWindowStart) {
            if (state.windowStartMillis >= 0
                    && currentWindowStart - state.windowStartMillis == windowMillis) {
                state.previousCounts = state.currentCounts.clone();
            } else {
                state.previousCounts = new int[subWindows];
            }
            state.currentCounts = new int[subWindows];
            state.windowStartMillis = currentWindowStart;
        } else if (currentSubWindowIndex > state.currentSubWindowIndex) {
            for (int i = state.currentSubWindowIndex + 1; i <= currentSubWindowIndex; i++) {
                state.currentCounts[i] = 0;
            }
        }

        state.currentSubWindowIndex = currentSubWindowIndex;
    }

    private double computeWeightedCount(SlidingWindowCounterState state) {
        int currentTotal = sum(state.currentCounts);
        int previousTotal = sum(state.previousCounts);
        long windowMillis = config.getWindow().toMillis();
        int subWindows = config.getSubWindows();
        long subWindowMillis = windowMillis / subWindows;

        if (subWindowMillis <= 0 || state.windowStartMillis < 0) {
            return currentTotal;
        }

        long elapsedInWindow = clock.millis() - state.windowStartMillis;
        double elapsedRatio = Math.min(1.0, (double) elapsedInWindow / windowMillis);
        double previousWeight = 1.0 - elapsedRatio;
        return currentTotal + (previousTotal * previousWeight);
    }

    private long computeRetryAfterSeconds(SlidingWindowCounterState state) {
        long windowMillis = config.getWindow().toMillis();
        int subWindows = config.getSubWindows();
        long subWindowMillis = windowMillis / subWindows;
        if (subWindowMillis <= 0) {
            return 1;
        }
        long nextSubWindowStart = state.windowStartMillis + ((long) (state.currentSubWindowIndex + 1) * subWindowMillis);
        long millisRemaining = nextSubWindowStart - clock.millis();
        return Math.max(1, (millisRemaining + 999) / 1000);
    }

    private int sum(int[] counts) {
        int total = 0;
        for (int count : counts) {
            total += count;
        }
        return total;
    }

    @Override
    public RateLimiterType getType() {
        return RateLimiterType.SLIDING_WINDOW_COUNTER;
    }

    private static final class SlidingWindowCounterState {
        private long windowStartMillis = -1;
        private int currentSubWindowIndex;
        private int[] currentCounts;
        private int[] previousCounts;

        private SlidingWindowCounterState(int subWindows) {
            this.currentCounts = new int[subWindows];
            this.previousCounts = new int[subWindows];
        }
    }
}
