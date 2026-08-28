package com.interviewprep.producerconsumer.executor;

import com.interviewprep.producerconsumer.buffer.BoundedBuffer;
import com.interviewprep.producerconsumer.model.WorkItem;

import java.time.Duration;
import java.util.Optional;
import java.util.concurrent.CountDownLatch;
import java.util.concurrent.ExecutorService;
import java.util.concurrent.atomic.AtomicBoolean;
import java.util.concurrent.atomic.AtomicInteger;
import java.util.concurrent.atomic.AtomicReference;
import java.util.logging.Level;
import java.util.logging.Logger;

final class ConsumerTask implements Runnable {

    private static final Logger LOGGER = Logger.getLogger(ConsumerTask.class.getName());

    private final int consumerId;
    private final int expectedTotalItems;
    private final BoundedBuffer<WorkItem> buffer;
    private final Duration pollTimeout;
    private final ExecutorService executor;
    private final AtomicInteger consumedCounter;
    private final CountDownLatch consumersDoneLatch;
    private final AtomicBoolean failed;
    private final AtomicReference<Throwable> failure;

    ConsumerTask(
            int consumerId,
            int expectedTotalItems,
            BoundedBuffer<WorkItem> buffer,
            Duration pollTimeout,
            ExecutorService executor,
            AtomicInteger consumedCounter,
            CountDownLatch consumersDoneLatch,
            AtomicBoolean failed,
            AtomicReference<Throwable> failure) {
        this.consumerId = consumerId;
        this.expectedTotalItems = expectedTotalItems;
        this.buffer = buffer;
        this.pollTimeout = pollTimeout;
        this.executor = executor;
        this.consumedCounter = consumedCounter;
        this.consumersDoneLatch = consumersDoneLatch;
        this.failed = failed;
        this.failure = failure;
    }

    @Override
    public void run() {
        tryConsume();
    }

    private void tryConsume() {
        if (failed.get()) {
            return;
        }

        if (consumedCounter.get() >= expectedTotalItems) {
            consumersDoneLatch.countDown();
            LOGGER.log(Level.INFO, "Consumer {0} finished", consumerId);
            return;
        }

        try {
            Optional<WorkItem> item = buffer.tryPoll(pollTimeout);
            if (item.isPresent()) {
                int totalConsumed = consumedCounter.incrementAndGet();
                LOGGER.log(Level.INFO, "Consumer {0} consumed {1} [total: {2}/{3}]",
                        new Object[] {consumerId, item.get(), totalConsumed, expectedTotalItems});
            }
            executor.execute(this::tryConsume);
        } catch (InterruptedException e) {
            Thread.currentThread().interrupt();
            recordFailure(e);
            consumersDoneLatch.countDown();
        } catch (RuntimeException e) {
            recordFailure(e);
            consumersDoneLatch.countDown();
        }
    }

    private void recordFailure(Throwable cause) {
        failed.set(true);
        failure.compareAndSet(null, cause);
        executor.shutdownNow();
        LOGGER.log(Level.SEVERE, "Consumer {0} failed", consumerId);
        LOGGER.log(Level.SEVERE, cause.getMessage(), cause);
    }
}
