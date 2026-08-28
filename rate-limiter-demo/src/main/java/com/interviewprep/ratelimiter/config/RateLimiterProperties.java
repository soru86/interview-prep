package com.interviewprep.ratelimiter.config;

import com.interviewprep.ratelimiter.model.RateLimiterType;
import jakarta.validation.Valid;
import jakarta.validation.constraints.Min;
import jakarta.validation.constraints.NotBlank;
import jakarta.validation.constraints.NotNull;
import org.springframework.boot.context.properties.ConfigurationProperties;
import org.springframework.validation.annotation.Validated;

import java.time.Duration;
import java.util.ArrayList;
import java.util.List;

@Validated
@ConfigurationProperties(prefix = "rate-limiter")
public class RateLimiterProperties {

    private boolean enabled = true;

    @NotNull
    private RateLimiterType type = RateLimiterType.TOKEN_BUCKET;

    @NotBlank
    private String keySource = "client-ip";

    private List<String> excludePaths = new ArrayList<>(List.of("/actuator/**"));

    @Valid
    @NotNull
    private TokenBucketProperties tokenBucket = new TokenBucketProperties();

    @Valid
    @NotNull
    private LeakyBucketProperties leakyBucket = new LeakyBucketProperties();

    @Valid
    @NotNull
    private WindowProperties fixedWindow = new WindowProperties();

    @Valid
    @NotNull
    private WindowProperties slidingWindowLog = new WindowProperties();

    @Valid
    @NotNull
    private SlidingWindowCounterProperties slidingWindowCounter = new SlidingWindowCounterProperties();

    public boolean isEnabled() {
        return enabled;
    }

    public void setEnabled(boolean enabled) {
        this.enabled = enabled;
    }

    public RateLimiterType getType() {
        return type;
    }

    public void setType(RateLimiterType type) {
        this.type = type;
    }

    public String getKeySource() {
        return keySource;
    }

    public void setKeySource(String keySource) {
        this.keySource = keySource;
    }

    public List<String> getExcludePaths() {
        return excludePaths;
    }

    public void setExcludePaths(List<String> excludePaths) {
        this.excludePaths = excludePaths;
    }

    public TokenBucketProperties getTokenBucket() {
        return tokenBucket;
    }

    public void setTokenBucket(TokenBucketProperties tokenBucket) {
        this.tokenBucket = tokenBucket;
    }

    public LeakyBucketProperties getLeakyBucket() {
        return leakyBucket;
    }

    public void setLeakyBucket(LeakyBucketProperties leakyBucket) {
        this.leakyBucket = leakyBucket;
    }

    public WindowProperties getFixedWindow() {
        return fixedWindow;
    }

    public void setFixedWindow(WindowProperties fixedWindow) {
        this.fixedWindow = fixedWindow;
    }

    public WindowProperties getSlidingWindowLog() {
        return slidingWindowLog;
    }

    public void setSlidingWindowLog(WindowProperties slidingWindowLog) {
        this.slidingWindowLog = slidingWindowLog;
    }

    public SlidingWindowCounterProperties getSlidingWindowCounter() {
        return slidingWindowCounter;
    }

    public void setSlidingWindowCounter(SlidingWindowCounterProperties slidingWindowCounter) {
        this.slidingWindowCounter = slidingWindowCounter;
    }

    public static class TokenBucketProperties {

        @Min(1)
        private int bucketSize = 10;

        @Min(1)
        private int refillRate = 5;

        @NotNull
        private Duration refillInterval = Duration.ofSeconds(1);

        public int getBucketSize() {
            return bucketSize;
        }

        public void setBucketSize(int bucketSize) {
            this.bucketSize = bucketSize;
        }

        public int getRefillRate() {
            return refillRate;
        }

        public void setRefillRate(int refillRate) {
            this.refillRate = refillRate;
        }

        public Duration getRefillInterval() {
            return refillInterval;
        }

        public void setRefillInterval(Duration refillInterval) {
            this.refillInterval = refillInterval;
        }
    }

    public static class LeakyBucketProperties {

        @Min(1)
        private int bucketSize = 10;

        @Min(1)
        private int leakRate = 2;

        @NotNull
        private Duration leakInterval = Duration.ofSeconds(1);

        public int getBucketSize() {
            return bucketSize;
        }

        public void setBucketSize(int bucketSize) {
            this.bucketSize = bucketSize;
        }

        public int getLeakRate() {
            return leakRate;
        }

        public void setLeakRate(int leakRate) {
            this.leakRate = leakRate;
        }

        public Duration getLeakInterval() {
            return leakInterval;
        }

        public void setLeakInterval(Duration leakInterval) {
            this.leakInterval = leakInterval;
        }
    }

    public static class WindowProperties {

        @Min(1)
        private int limit = 100;

        @NotNull
        private Duration window = Duration.ofMinutes(1);

        public int getLimit() {
            return limit;
        }

        public void setLimit(int limit) {
            this.limit = limit;
        }

        public Duration getWindow() {
            return window;
        }

        public void setWindow(Duration window) {
            this.window = window;
        }
    }

    public static class SlidingWindowCounterProperties extends WindowProperties {

        @Min(1)
        private int subWindows = 10;

        public int getSubWindows() {
            return subWindows;
        }

        public void setSubWindows(int subWindows) {
            this.subWindows = subWindows;
        }
    }
}
