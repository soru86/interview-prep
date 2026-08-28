package com.interviewprep.ratelimiter.strategy;

import com.interviewprep.ratelimiter.model.RateLimiterDecision;
import com.interviewprep.ratelimiter.model.RateLimiterType;

public interface RateLimiterStrategy {

    RateLimiterDecision tryConsume(String key);

    RateLimiterType getType();
}
