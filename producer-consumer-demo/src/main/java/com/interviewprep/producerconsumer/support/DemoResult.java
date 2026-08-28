package com.interviewprep.producerconsumer.support;

import com.interviewprep.producerconsumer.config.DemoConfig;

public record DemoResult(
        String demoName,
        int produced,
        int consumed,
        int expected,
        long durationMs,
        DemoConfig config,
        boolean success) {

    public void printSummary() {
        System.out.println();
        System.out.println("=== " + demoName + " Complete ===");
        System.out.printf("Produced: %d, Consumed: %d, Expected: %d, Duration: %dms%n",
                produced, consumed, expected, durationMs);
        System.out.printf(
                "Pool size: %d, Buffer: %d, Producers: %d, Consumers: %d%n",
                config.poolSize(),
                config.bufferCapacity(),
                config.producerCount(),
                config.consumerCount());
        if (!success) {
            System.err.println("FAILED: produced/consumed counts do not match expected total.");
        }
    }
}
