package com.interviewprep.virtualthreaddemo;

import java.time.Duration;
import java.time.Instant;
import java.util.concurrent.atomic.AtomicBoolean;
import java.util.concurrent.atomic.AtomicLong;

final class DemoRuntime {

    static final int POOL_SIZE = 20_000;
    static final int PRODUCER_COUNT = 10_000;
    static final int CONSUMER_COUNT = 10_000;
    static final int QUEUE_CAPACITY = 20_000;
    static final Duration STATS_INTERVAL = Duration.ofSeconds(30);
    static final Duration SHUTDOWN_TIMEOUT = Duration.ofSeconds(30);

    final AtomicBoolean running = new AtomicBoolean(true);
    final AtomicLong sequenceGenerator = new AtomicLong();
    final AtomicLong producedCount = new AtomicLong();
    final AtomicLong consumedCount = new AtomicLong();
    final AtomicLong producerErrorCount = new AtomicLong();
    final AtomicLong consumerErrorCount = new AtomicLong();
    final Instant deadline;

    DemoRuntime(Instant deadline) {
        this.deadline = deadline;
    }

    boolean isActive() {
        return running.get() && !Instant.now().isAfter(deadline);
    }

    void stop() {
        running.set(false);
    }

    static Duration resolveDuration() {
        String secondsOverride = System.getProperty("demo.duration.seconds");
        if (secondsOverride != null && !secondsOverride.isBlank()) {
            return Duration.ofSeconds(Long.parseLong(secondsOverride.trim()));
        }
        int minutes = Integer.getInteger("demo.duration.minutes", 15);
        return Duration.ofMinutes(minutes);
    }
}
