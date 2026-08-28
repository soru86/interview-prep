package com.interviewprep.producerconsumer.virtualthread;

import com.interviewprep.producerconsumer.buffer.BoundedBuffer;
import com.interviewprep.producerconsumer.model.WorkItem;

import java.util.concurrent.atomic.AtomicBoolean;
import java.util.concurrent.atomic.AtomicInteger;
import java.util.concurrent.atomic.AtomicReference;
import java.util.logging.Level;
import java.util.logging.Logger;

final class VirtualConsumerTask implements Runnable {

    private static final Logger LOGGER = Logger.getLogger(VirtualConsumerTask.class.getName());

    private final int consumerId;
    private final int itemsToConsume;
    private final BoundedBuffer<WorkItem> buffer;
    private final AtomicInteger consumedCounter;
    private final int expectedTotalItems;
    private final AtomicBoolean failed;
    private final AtomicReference<Throwable> failure;

    VirtualConsumerTask(
            int consumerId,
            int itemsToConsume,
            BoundedBuffer<WorkItem> buffer,
            AtomicInteger consumedCounter,
            int expectedTotalItems,
            AtomicBoolean failed,
            AtomicReference<Throwable> failure) {
        this.consumerId = consumerId;
        this.itemsToConsume = itemsToConsume;
        this.buffer = buffer;
        this.consumedCounter = consumedCounter;
        this.expectedTotalItems = expectedTotalItems;
        this.failed = failed;
        this.failure = failure;
    }

    @Override
    public void run() {
        try {
            for (int i = 0; i < itemsToConsume; i++) {
                if (failed.get()) {
                    return;
                }
                WorkItem item = buffer.take();
                int totalConsumed = consumedCounter.incrementAndGet();
                LOGGER.log(Level.INFO, "Consumer {0} consumed {1} [total: {2}/{3}]",
                        new Object[] {consumerId, item, totalConsumed, expectedTotalItems});
            }
            LOGGER.log(Level.INFO, "Consumer {0} finished", consumerId);
        } catch (InterruptedException e) {
            Thread.currentThread().interrupt();
            recordFailure(e);
        } catch (RuntimeException e) {
            recordFailure(e);
        }
    }

    private void recordFailure(Throwable cause) {
        failed.set(true);
        failure.compareAndSet(null, cause);
        LOGGER.log(Level.SEVERE, "Virtual consumer {0} failed", consumerId);
        LOGGER.log(Level.SEVERE, cause.getMessage(), cause);
    }
}
