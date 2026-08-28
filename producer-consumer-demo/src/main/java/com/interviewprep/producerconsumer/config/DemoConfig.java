package com.interviewprep.producerconsumer.config;

import java.time.Duration;

public record DemoConfig(
        int poolSize,
        int bufferCapacity,
        int producerCount,
        int consumerCount,
        int itemsPerProducer,
        long offerPollTimeoutMs) {

    public static final DemoConfig DEFAULT = new DemoConfig(4, 5, 3, 3, 10, 50);

    public DemoConfig {
        if (poolSize < 2) {
            throw new IllegalArgumentException("poolSize must be at least 2, got: " + poolSize);
        }
        if (bufferCapacity < 1) {
            throw new IllegalArgumentException("bufferCapacity must be at least 1, got: " + bufferCapacity);
        }
        if (producerCount < 1) {
            throw new IllegalArgumentException("producerCount must be at least 1, got: " + producerCount);
        }
        if (consumerCount < 1) {
            throw new IllegalArgumentException("consumerCount must be at least 1, got: " + consumerCount);
        }
        if (itemsPerProducer < 1) {
            throw new IllegalArgumentException("itemsPerProducer must be at least 1, got: " + itemsPerProducer);
        }
        if (offerPollTimeoutMs < 1) {
            throw new IllegalArgumentException("offerPollTimeoutMs must be at least 1, got: " + offerPollTimeoutMs);
        }
    }

    public int expectedTotalItems() {
        return producerCount * itemsPerProducer;
    }

    public Duration offerPollTimeout() {
        return Duration.ofMillis(offerPollTimeoutMs);
    }

    public DemoConfig withPoolSize(int newPoolSize) {
        return new DemoConfig(
                newPoolSize,
                bufferCapacity,
                producerCount,
                consumerCount,
                itemsPerProducer,
                offerPollTimeoutMs);
    }

    @Override
    public String toString() {
        return "DemoConfig{"
                + "poolSize=" + poolSize
                + ", bufferCapacity=" + bufferCapacity
                + ", producerCount=" + producerCount
                + ", consumerCount=" + consumerCount
                + ", itemsPerProducer=" + itemsPerProducer
                + ", offerPollTimeoutMs=" + offerPollTimeoutMs
                + '}';
    }
}
