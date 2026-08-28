package com.interviewprep.ratelimiter.config;

import com.fasterxml.jackson.databind.ObjectMapper;
import com.interviewprep.ratelimiter.factory.RateLimiterStrategyFactory;
import com.interviewprep.ratelimiter.filter.RateLimiterFilter;
import com.interviewprep.ratelimiter.support.ClientKeyResolver;
import org.springframework.boot.web.servlet.FilterRegistrationBean;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import org.springframework.util.AntPathMatcher;

import java.time.Clock;

@Configuration
public class RateLimiterConfig {

    @Bean
    public Clock clock() {
        return Clock.systemUTC();
    }

    @Bean
    public AntPathMatcher antPathMatcher() {
        return new AntPathMatcher();
    }

    @Bean
    public FilterRegistrationBean<RateLimiterFilter> rateLimiterFilterRegistration(
            RateLimiterProperties properties,
            RateLimiterStrategyFactory strategyFactory,
            ClientKeyResolver clientKeyResolver,
            AntPathMatcher pathMatcher,
            ObjectMapper objectMapper) {
        FilterRegistrationBean<RateLimiterFilter> registration = new FilterRegistrationBean<>();
        registration.setFilter(new RateLimiterFilter(
                properties,
                strategyFactory,
                clientKeyResolver,
                pathMatcher,
                objectMapper));
        registration.addUrlPatterns("/*");
        registration.setOrder(1);
        return registration;
    }
}
