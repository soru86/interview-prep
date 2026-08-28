package com.interviewprep.producerconsumer.virtualthread;

import com.interviewprep.producerconsumer.buffer.BoundedBuffer;
import com.interviewprep.producerconsumer.config.DemoConfig;
import com.interviewprep.producerconsumer.model.WorkItem;
import com.interviewprep.producerconsumer.support.DemoResult;
import com.interviewprep.producerconsumer.support.ShutdownSupport;

import java.time.Duration;
import java.util.ArrayList;
import java.util.List;
import java.util.concurrent.ExecutorService;
import java.util.concurrent.Executors;
import java.util.concurrent.Future;
import java.util.concurrent.TimeUnit;
import java.util.concurrent.atomic.AtomicBoolean;
import java.util.concurrent.atomic.AtomicInteger;
import java.util.concurrent.atomic.AtomicReference;
import java.util.logging.Logger;

public final class ProducerConsumerVirtualThreadDemo {

    private static final Logger LOGGER = Logger.getLogger(ProducerConsumerVirtualThreadDemo.class.getName());
    private static final Duration SHUTDOWN_TIMEOUT = Duration.ofSeconds(5);

    private final DemoConfig config;

    public ProducerConsumerVirtualThreadDemo(DemoConfig config) {
        this.config = config;
    }

    public DemoResult run() throws InterruptedException {
        LOGGER.info("Starting virtual-thread demo with config: " + config);

        BoundedBuffer<WorkItem> buffer = new BoundedBuffer<>(config.bufferCapacity());
        AtomicInteger producedCounter = new AtomicInteger();
        AtomicInteger consumedCounter = new AtomicInteger();
        AtomicBoolean failed = new AtomicBoolean();
        AtomicReference<Throwable> failure = new AtomicReference<>();

        ExecutorService executor = Executors.newVirtualThreadPerTaskExecutor();
        long startNanos = System.nanoTime();

        try {
            List<Future<?>> futures = new ArrayList<>();

            for (int i = 0; i < config.producerCount(); i++) {
                futures.add(executor.submit(new VirtualProducerTask(
                        i,
                        config.itemsPerProducer(),
                        buffer,
                        producedCounter,
                        failed,
                        failure)));
            }

            int expectedTotal = config.expectedTotalItems();
            int baseItemsPerConsumer = expectedTotal / config.consumerCount();
            int remainder = expectedTotal % config.consumerCount();

            for (int i = 0; i < config.consumerCount(); i++) {
                int itemsForConsumer = baseItemsPerConsumer + (i < remainder ? 1 : 0);
                futures.add(executor.submit(new VirtualConsumerTask(
                        i,
                        itemsForConsumer,
                        buffer,
                        consumedCounter,
                        expectedTotal,
                        failed,
                        failure)));
            }

            for (Future<?> future : futures) {
                try {
                    future.get(2, TimeUnit.MINUTES);
                } catch (Exception e) {
                    failed.set(true);
                    failure.compareAndSet(null, e);
                    throw new IllegalStateException("Virtual-thread demo task failed", e);
                }
            }
        } finally {
            ShutdownSupport.gracefulShutdown(executor, SHUTDOWN_TIMEOUT);
        }

        long durationMs = TimeUnit.NANOSECONDS.toMillis(System.nanoTime() - startNanos);

        if (failure.get() != null) {
            throw new IllegalStateException("Virtual-thread demo failed", failure.get());
        }

        int expectedTotal = config.expectedTotalItems();
        int produced = producedCounter.get();
        int consumed = consumedCounter.get();
        boolean success = produced == expectedTotal && consumed == expectedTotal;

        return new DemoResult(
                "Virtual Thread Demo",
                produced,
                consumed,
                expectedTotal,
                durationMs,
                config,
                success);
    }
}
