package com.interviewprep.producerconsumer.executor;

import com.interviewprep.producerconsumer.buffer.BoundedBuffer;
import com.interviewprep.producerconsumer.config.DemoConfig;
import com.interviewprep.producerconsumer.model.WorkItem;
import com.interviewprep.producerconsumer.support.DemoResult;
import com.interviewprep.producerconsumer.support.ShutdownSupport;

import java.time.Duration;
import java.util.concurrent.CountDownLatch;
import java.util.concurrent.ExecutorService;
import java.util.concurrent.Executors;
import java.util.concurrent.ThreadFactory;
import java.util.concurrent.TimeUnit;
import java.util.concurrent.atomic.AtomicBoolean;
import java.util.concurrent.atomic.AtomicInteger;
import java.util.concurrent.atomic.AtomicReference;
import java.util.logging.Level;
import java.util.logging.Logger;

public final class ProducerConsumerExecutorDemo {

    private static final Logger LOGGER = Logger.getLogger(ProducerConsumerExecutorDemo.class.getName());
    private static final Duration SHUTDOWN_TIMEOUT = Duration.ofSeconds(5);

    private final DemoConfig config;

    public ProducerConsumerExecutorDemo(DemoConfig config) {
        this.config = config;
    }

    public DemoResult run() throws InterruptedException {
        LOGGER.info("Starting executor demo with config: " + config);

        BoundedBuffer<WorkItem> buffer = new BoundedBuffer<>(config.bufferCapacity());
        AtomicInteger producedCounter = new AtomicInteger();
        AtomicInteger consumedCounter = new AtomicInteger();
        AtomicBoolean failed = new AtomicBoolean();
        AtomicReference<Throwable> failure = new AtomicReference<>();

        CountDownLatch producersDoneLatch = new CountDownLatch(config.producerCount());
        CountDownLatch consumersDoneLatch = new CountDownLatch(config.consumerCount());

        ThreadFactory threadFactory = runnable -> {
            Thread thread = new Thread(runnable);
            thread.setName("pool-worker");
            thread.setUncaughtExceptionHandler((t, e) -> {
                failed.set(true);
                failure.compareAndSet(null, e);
                LOGGER.log(Level.SEVERE, "Uncaught exception in " + t.getName(), e);
            });
            return thread;
        };

        ExecutorService executor = Executors.newFixedThreadPool(config.poolSize(), threadFactory);

        long startNanos = System.nanoTime();

        try {
            for (int i = 0; i < config.producerCount(); i++) {
                executor.execute(new ProducerTask(
                        i,
                        config.itemsPerProducer(),
                        buffer,
                        config.offerPollTimeout(),
                        executor,
                        producedCounter,
                        producersDoneLatch,
                        failed,
                        failure));
            }

            for (int i = 0; i < config.consumerCount(); i++) {
                executor.execute(new ConsumerTask(
                        i,
                        config.expectedTotalItems(),
                        buffer,
                        config.offerPollTimeout(),
                        executor,
                        consumedCounter,
                        consumersDoneLatch,
                        failed,
                        failure));
            }

            if (!producersDoneLatch.await(2, TimeUnit.MINUTES)) {
                throw new IllegalStateException("Producers did not finish within timeout");
            }
            if (!consumersDoneLatch.await(2, TimeUnit.MINUTES)) {
                throw new IllegalStateException("Consumers did not finish within timeout");
            }
        } finally {
            ShutdownSupport.gracefulShutdown(executor, SHUTDOWN_TIMEOUT);
        }

        long durationMs = TimeUnit.NANOSECONDS.toMillis(System.nanoTime() - startNanos);

        if (failure.get() != null) {
            throw new IllegalStateException("Executor demo failed", failure.get());
        }

        int produced = producedCounter.get();
        int consumed = consumedCounter.get();
        int expected = config.expectedTotalItems();
        boolean success = produced == expected && consumed == expected;

        return new DemoResult(
                "Executor Demo",
                produced,
                consumed,
                expected,
                durationMs,
                config,
                success);
    }
}
