package com.interviewprep.producerconsumer.executor;

import com.interviewprep.producerconsumer.buffer.BoundedBuffer;
import com.interviewprep.producerconsumer.model.WorkItem;

import java.time.Duration;
import java.util.concurrent.CountDownLatch;
import java.util.concurrent.ExecutorService;
import java.util.concurrent.atomic.AtomicBoolean;
import java.util.concurrent.atomic.AtomicInteger;
import java.util.concurrent.atomic.AtomicReference;
import java.util.logging.Level;
import java.util.logging.Logger;

final class ProducerTask implements Runnable {

    private static final Logger LOGGER = Logger.getLogger(ProducerTask.class.getName());

    private final int producerId;
    private final int itemsToProduce;
    private final BoundedBuffer<WorkItem> buffer;
    private final Duration offerTimeout;
    private final ExecutorService executor;
    private final AtomicInteger producedCounter;
    private final AtomicInteger nextItemNumber;
    private final CountDownLatch producersDoneLatch;
    private final AtomicBoolean failed;
    private final AtomicReference<Throwable> failure;

    ProducerTask(
            int producerId,
            int itemsToProduce,
            BoundedBuffer<WorkItem> buffer,
            Duration offerTimeout,
            ExecutorService executor,
            AtomicInteger producedCounter,
            CountDownLatch producersDoneLatch,
            AtomicBoolean failed,
            AtomicReference<Throwable> failure) {
        this.producerId = producerId;
        this.itemsToProduce = itemsToProduce;
        this.buffer = buffer;
        this.offerTimeout = offerTimeout;
        this.executor = executor;
        this.producedCounter = producedCounter;
        this.nextItemNumber = new AtomicInteger(0);
        this.producersDoneLatch = producersDoneLatch;
        this.failed = failed;
        this.failure = failure;
    }

    @Override
    public void run() {
        tryProduce();
    }

    private void tryProduce() {
        if (failed.get()) {
            return;
        }

        int itemNumber = nextItemNumber.get();
        if (itemNumber >= itemsToProduce) {
            producersDoneLatch.countDown();
            LOGGER.log(Level.INFO, "Producer {0} finished", producerId);
            return;
        }

        WorkItem item = new WorkItem(producerId, itemNumber);

        try {
            if (buffer.tryOffer(item, offerTimeout)) {
                nextItemNumber.incrementAndGet();
                producedCounter.incrementAndGet();
                LOGGER.log(Level.INFO, "Produced {0} [buffer: {1}/{2}]",
                        new Object[] {item, buffer.size(), buffer.capacity()});
            }
            executor.execute(this::tryProduce);
        } catch (InterruptedException e) {
            Thread.currentThread().interrupt();
            recordFailure(e);
            producersDoneLatch.countDown();
        } catch (RuntimeException e) {
            recordFailure(e);
            producersDoneLatch.countDown();
        }
    }

    private void recordFailure(Throwable cause) {
        failed.set(true);
        failure.compareAndSet(null, cause);
        executor.shutdownNow();
        LOGGER.log(Level.SEVERE, "Producer {0} failed", producerId);
        LOGGER.log(Level.SEVERE, cause.getMessage(), cause);
    }
}
