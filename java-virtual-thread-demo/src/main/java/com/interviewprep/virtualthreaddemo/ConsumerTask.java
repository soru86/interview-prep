package com.interviewprep.virtualthreaddemo;

import java.util.concurrent.BlockingQueue;
import java.util.concurrent.TimeUnit;
import java.util.logging.Level;
import java.util.logging.Logger;

final class ConsumerTask implements Runnable {

    private static final Logger LOGGER = Logger.getLogger(ConsumerTask.class.getName());
    private static final long POLL_TIMEOUT_MS = 250;

    private final int consumerId;
    private final BlockingQueue<DataItem> queue;
    private final DemoRuntime runtime;

    ConsumerTask(int consumerId, BlockingQueue<DataItem> queue, DemoRuntime runtime) {
        this.consumerId = consumerId;
        this.queue = queue;
        this.runtime = runtime;
    }

    @Override
    public void run() {
        Thread currentThread = Thread.currentThread();

        while (runtime.isActive() || !queue.isEmpty()) {
            try {
                DataItem item = queue.poll(POLL_TIMEOUT_MS, TimeUnit.MILLISECONDS);
                if (item == null) {
                    continue;
                }

                runtime.consumedCount.incrementAndGet();

                LOGGER.log(
                        Level.INFO,
                        "[CONSUMER] threadId={0} threadName={1} consumerId={2} data={3} queueSize={4}",
                        new Object[] {
                            currentThread.threadId(),
                            currentThread.getName(),
                            consumerId,
                            item,
                            queue.size()
                        });
            } catch (InterruptedException e) {
                Thread.currentThread().interrupt();
                LOGGER.log(Level.INFO, "[CONSUMER] consumerId={0} interrupted, stopping", consumerId);
                return;
            } catch (RuntimeException e) {
                runtime.consumerErrorCount.incrementAndGet();
                LOGGER.log(
                        Level.WARNING,
                        "[CONSUMER] consumerId={0} threadId={1} recovered from error, continuing",
                        new Object[] {consumerId, currentThread.threadId()});
                LOGGER.log(Level.WARNING, e.getMessage(), e);
            }
        }

        LOGGER.log(Level.INFO, "[CONSUMER] consumerId={0} finished", consumerId);
    }
}
