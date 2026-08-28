package com.interviewprep.virtualthreaddemo;

import java.time.Instant;
import java.util.concurrent.BlockingQueue;
import java.util.logging.Level;
import java.util.logging.Logger;

final class ProducerTask implements Runnable {

    private static final Logger LOGGER = Logger.getLogger(ProducerTask.class.getName());

    private final int producerId;
    private final BlockingQueue<DataItem> queue;
    private final DemoRuntime runtime;

    ProducerTask(int producerId, BlockingQueue<DataItem> queue, DemoRuntime runtime) {
        this.producerId = producerId;
        this.queue = queue;
        this.runtime = runtime;
    }

    @Override
    public void run() {
        long localSequence = 0;
        Thread currentThread = Thread.currentThread();

        while (runtime.isActive()) {
            try {
                DataItem item = new DataItem(
                        runtime.sequenceGenerator.incrementAndGet(),
                        producerId,
                        "payload-p" + producerId + "-n" + (++localSequence),
                        Instant.now());

                queue.put(item);
                runtime.producedCount.incrementAndGet();

                LOGGER.log(
                        Level.INFO,
                        "[PRODUCER] threadId={0} threadName={1} producerId={2} data={3} queueSize={4}",
                        new Object[] {
                            currentThread.threadId(),
                            currentThread.getName(),
                            producerId,
                            item,
                            queue.size()
                        });
            } catch (InterruptedException e) {
                Thread.currentThread().interrupt();
                LOGGER.log(Level.INFO, "[PRODUCER] producerId={0} interrupted, stopping", producerId);
                return;
            } catch (RuntimeException e) {
                runtime.producerErrorCount.incrementAndGet();
                LOGGER.log(
                        Level.WARNING,
                        "[PRODUCER] producerId={0} threadId={1} recovered from error, continuing",
                        new Object[] {producerId, currentThread.threadId()});
                LOGGER.log(Level.WARNING, e.getMessage(), e);
            }
        }

        LOGGER.log(Level.INFO, "[PRODUCER] producerId={0} finished", producerId);
    }
}
