package com.interviewprep.ratelimiter.factory;

import com.interviewprep.ratelimiter.config.RateLimiterProperties;
import com.interviewprep.ratelimiter.model.RateLimiterType;
import com.interviewprep.ratelimiter.strategy.RateLimiterStrategy;
import jakarta.annotation.PostConstruct;
import org.springframework.stereotype.Component;

import java.util.EnumMap;
import java.util.List;
import java.util.Map;

@Component
public class RateLimiterStrategyFactory {

    private final RateLimiterProperties properties;
    private final Map<RateLimiterType, RateLimiterStrategy> strategiesByType = new EnumMap<>(RateLimiterType.class);

    public RateLimiterStrategyFactory(
            RateLimiterProperties properties,
            List<RateLimiterStrategy> strategies) {
        this.properties = properties;
        for (RateLimiterStrategy strategy : strategies) {
            strategiesByType.put(strategy.getType(), strategy);
        }
    }

    @PostConstruct
    void validateActiveStrategy() {
        RateLimiterType activeType = properties.getType();
        if (!strategiesByType.containsKey(activeType)) {
            throw new IllegalStateException("No rate limiter strategy registered for type: " + activeType);
        }
    }

    public RateLimiterStrategy getActiveStrategy() {
        RateLimiterStrategy strategy = strategiesByType.get(properties.getType());
        if (strategy == null) {
            throw new IllegalStateException("No rate limiter strategy registered for type: " + properties.getType());
        }
        return strategy;
    }
}
