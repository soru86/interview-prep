package com.interviewprep.ratelimiter.filter;

import com.fasterxml.jackson.databind.ObjectMapper;
import com.interviewprep.ratelimiter.config.RateLimiterProperties;
import com.interviewprep.ratelimiter.factory.RateLimiterStrategyFactory;
import com.interviewprep.ratelimiter.model.RateLimiterDecision;
import com.interviewprep.ratelimiter.strategy.RateLimiterStrategy;
import com.interviewprep.ratelimiter.support.ClientKeyResolver;
import jakarta.servlet.FilterChain;
import jakarta.servlet.ServletException;
import jakarta.servlet.http.HttpServletRequest;
import jakarta.servlet.http.HttpServletResponse;
import org.springframework.http.HttpStatus;
import org.springframework.http.MediaType;
import org.springframework.util.AntPathMatcher;
import org.springframework.web.filter.OncePerRequestFilter;

import java.io.IOException;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Map;

public class RateLimiterFilter extends OncePerRequestFilter {

    private final RateLimiterProperties properties;
    private final RateLimiterStrategyFactory strategyFactory;
    private final ClientKeyResolver clientKeyResolver;
    private final AntPathMatcher pathMatcher;
    private final ObjectMapper objectMapper;

    public RateLimiterFilter(
            RateLimiterProperties properties,
            RateLimiterStrategyFactory strategyFactory,
            ClientKeyResolver clientKeyResolver,
            AntPathMatcher pathMatcher,
            ObjectMapper objectMapper) {
        this.properties = properties;
        this.strategyFactory = strategyFactory;
        this.clientKeyResolver = clientKeyResolver;
        this.pathMatcher = pathMatcher;
        this.objectMapper = objectMapper;
    }

    @Override
    protected boolean shouldNotFilter(HttpServletRequest request) {
        if (!properties.isEnabled()) {
            return true;
        }
        String path = request.getRequestURI();
        List<String> excludePaths = properties.getExcludePaths();
        for (String pattern : excludePaths) {
            if (pathMatcher.match(pattern, path)) {
                return true;
            }
        }
        return false;
    }

    @Override
    protected void doFilterInternal(
            HttpServletRequest request,
            HttpServletResponse response,
            FilterChain filterChain) throws ServletException, IOException {
        String clientKey = clientKeyResolver.resolve(request);
        RateLimiterStrategy strategy = strategyFactory.getActiveStrategy();
        RateLimiterDecision decision = strategy.tryConsume(clientKey);

        response.setHeader("X-RateLimit-Limit", String.valueOf(decision.limit()));
        response.setHeader("X-RateLimit-Remaining", String.valueOf(decision.remaining()));

        if (!decision.allowed()) {
            response.setStatus(HttpStatus.TOO_MANY_REQUESTS.value());
            response.setHeader("Retry-After", String.valueOf(decision.retryAfterSeconds()));
            response.setContentType(MediaType.APPLICATION_JSON_VALUE);

            Map<String, Object> body = new LinkedHashMap<>();
            body.put("error", "Too Many Requests");
            body.put("message", "Rate limit exceeded");
            body.put("retryAfterSeconds", decision.retryAfterSeconds());
            objectMapper.writeValue(response.getOutputStream(), body);
            return;
        }

        filterChain.doFilter(request, response);
    }
}
