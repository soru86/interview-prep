package com.interviewprep.producerconsumer.virtualthread;

import com.interviewprep.producerconsumer.buffer.BoundedBuffer;
import com.interviewprep.producerconsumer.model.WorkItem;

import java.util.concurrent.atomic.AtomicBoolean;
import java.util.concurrent.atomic.AtomicInteger;
import java.util.concurrent.atomic.AtomicReference;
import java.util.logging.Level;
import java.util.logging.Logger;

final class VirtualProducerTask implements Runnable {

    private static final Logger LOGGER = Logger.getLogger(VirtualProducerTask.class.getName());

    private final int producerId;
    private final int itemsToProduce;
    private final BoundedBuffer<WorkItem> buffer;
    private final AtomicInteger producedCounter;
    private final AtomicBoolean failed;
    private final AtomicReference<Throwable> failure;

    VirtualProducerTask(
            int producerId,
            int itemsToProduce,
            BoundedBuffer<WorkItem> buffer,
            AtomicInteger producedCounter,
            AtomicBoolean failed,
            AtomicReference<Throwable> failure) {
        this.producerId = producerId;
        this.itemsToProduce = itemsToProduce;
        this.buffer = buffer;
        this.producedCounter = producedCounter;
        this.failed = failed;
        this.failure = failure;
    }

    @Override
    public void run() {
        try {
            for (int itemNumber = 0; itemNumber < itemsToProduce; itemNumber++) {
                if (failed.get()) {
                    return;
                }
                WorkItem item = new WorkItem(producerId, itemNumber);
                buffer.put(item);
                producedCounter.incrementAndGet();
                LOGGER.log(Level.INFO, "Produced {0} [buffer: {1}/{2}]",
                        new Object[] {item, buffer.size(), buffer.capacity()});
            }
            LOGGER.log(Level.INFO, "Producer {0} finished", producerId);
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
        LOGGER.log(Level.SEVERE, "Virtual producer {0} failed", producerId);
        LOGGER.log(Level.SEVERE, cause.getMessage(), cause);
    }
}
