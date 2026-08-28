package com.interviewprep.ratelimiter.config;

import com.interviewprep.ratelimiter.model.RateLimiterType;
import org.springframework.boot.context.properties.ConfigurationPropertiesBinding;
import org.springframework.core.convert.converter.Converter;
import org.springframework.stereotype.Component;

@Component
@ConfigurationPropertiesBinding
public class RateLimiterTypeConverter implements Converter<String, RateLimiterType> {

    @Override
    public RateLimiterType convert(String source) {
        return RateLimiterType.fromConfigValue(source);
    }
}
