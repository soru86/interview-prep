package com.interviewprep.ratelimiter.support;

import com.interviewprep.ratelimiter.config.RateLimiterProperties;
import jakarta.servlet.http.HttpServletRequest;
import org.springframework.stereotype.Component;
import org.springframework.util.StringUtils;

@Component
public class ClientKeyResolver {

    private static final String CLIENT_IP_PREFIX = "client-ip";
    private static final String HEADER_PREFIX = "header:";

    private final RateLimiterProperties properties;

    public ClientKeyResolver(RateLimiterProperties properties) {
        this.properties = properties;
    }

    public String resolve(HttpServletRequest request) {
        String keySource = properties.getKeySource();
        if (keySource.equalsIgnoreCase(CLIENT_IP_PREFIX)) {
            return resolveClientIp(request);
        }
        if (keySource.regionMatches(true, 0, HEADER_PREFIX, 0, HEADER_PREFIX.length())) {
            String headerName = keySource.substring(HEADER_PREFIX.length()).trim();
            String headerValue = request.getHeader(headerName);
            if (StringUtils.hasText(headerValue)) {
                return headerName + ":" + headerValue;
            }
            return "anonymous";
        }
        throw new IllegalStateException("Unsupported key source: " + keySource);
    }

    private String resolveClientIp(HttpServletRequest request) {
        String forwardedFor = request.getHeader("X-Forwarded-For");
        if (StringUtils.hasText(forwardedFor)) {
            return forwardedFor.split(",")[0].trim();
        }
        String remoteAddr = request.getRemoteAddr();
        return StringUtils.hasText(remoteAddr) ? remoteAddr : "unknown";
    }
}
