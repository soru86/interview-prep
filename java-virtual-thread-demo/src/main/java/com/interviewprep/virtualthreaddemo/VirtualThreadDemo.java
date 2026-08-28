package com.interviewprep.virtualthreaddemo;

import java.time.Duration;
import java.time.Instant;
import java.util.ArrayList;
import java.util.List;
import java.util.concurrent.ArrayBlockingQueue;
import java.util.concurrent.BlockingQueue;
import java.util.concurrent.ExecutorService;
import java.util.concurrent.Executors;
import java.util.concurrent.Future;
import java.util.concurrent.ScheduledExecutorService;
import java.util.concurrent.ThreadFactory;
import java.util.concurrent.TimeUnit;
import java.util.logging.ConsoleHandler;
import java.util.logging.Formatter;
import java.util.logging.Level;
import java.util.logging.LogRecord;
import java.util.logging.Logger;

public final class VirtualThreadDemo {

    private static final Logger LOGGER = Logger.getLogger(VirtualThreadDemo.class.getName());

    public static void main(String[] args) {
        configureLogging();
        installUncaughtExceptionHandler();

        Duration duration = DemoRuntime.resolveDuration();
        Instant deadline = Instant.now().plus(duration);
        DemoRuntime runtime = new DemoRuntime(deadline);

        BlockingQueue<DataItem> queue = new ArrayBlockingQueue<>(DemoRuntime.QUEUE_CAPACITY);
        ThreadFactory virtualThreadFactory = createVirtualThreadFactory();

        ExecutorService workerPool =
                Executors.newFixedThreadPool(DemoRuntime.POOL_SIZE, virtualThreadFactory);
        ScheduledExecutorService scheduler = Executors.newSingleThreadScheduledExecutor(r -> {
            Thread thread = new Thread(r, "demo-scheduler");
            thread.setDaemon(true);
            return thread;
        });

        long startNanos = System.nanoTime();

        LOGGER.info(() -> String.format(
                "Starting virtual-thread demo | poolSize=%d producers=%d consumers=%d queueCapacity=%d duration=%s deadline=%s",
                DemoRuntime.POOL_SIZE,
                DemoRuntime.PRODUCER_COUNT,
                DemoRuntime.CONSUMER_COUNT,
                DemoRuntime.QUEUE_CAPACITY,
                duration,
                deadline));

        List<Future<?>> futures = new ArrayList<>(DemoRuntime.PRODUCER_COUNT + DemoRuntime.CONSUMER_COUNT);

        try {
            scheduler.scheduleAtFixedRate(
                    () -> logStats(runtime, queue),
                    DemoRuntime.STATS_INTERVAL.toSeconds(),
                    DemoRuntime.STATS_INTERVAL.toSeconds(),
                    TimeUnit.SECONDS);

            scheduler.schedule(
                    () -> {
                        runtime.stop();
                        LOGGER.info("Demo duration elapsed; stopping producers and consumers.");
                    },
                    duration.toMillis(),
                    TimeUnit.MILLISECONDS);

            for (int producerId = 0; producerId < DemoRuntime.PRODUCER_COUNT; producerId++) {
                futures.add(workerPool.submit(new ProducerTask(producerId, queue, runtime)));
            }

            for (int consumerId = 0; consumerId < DemoRuntime.CONSUMER_COUNT; consumerId++) {
                futures.add(workerPool.submit(new ConsumerTask(consumerId, queue, runtime)));
            }

            awaitTasks(futures);
        } catch (Exception e) {
            LOGGER.log(Level.SEVERE, "Top-level demo failure", e);
        } finally {
            runtime.stop();
            shutdownExecutor(scheduler, Duration.ofSeconds(5));
            shutdownExecutor(workerPool, DemoRuntime.SHUTDOWN_TIMEOUT);
            logFinalSummary(runtime, queue, startNanos);
        }
    }

    private static ThreadFactory createVirtualThreadFactory() {
        return Thread.ofVirtual()
                .name("vt-", 0)
                .uncaughtExceptionHandler(
                        (thread, error) -> LOGGER.log(
                                Level.SEVERE,
                                "Uncaught exception on thread " + thread.getName()
                                        + " (id=" + thread.threadId() + ")",
                                error))
                .factory();
    }

    private static void installUncaughtExceptionHandler() {
        Thread.setDefaultUncaughtExceptionHandler(
                (thread, error) -> LOGGER.log(
                        Level.SEVERE,
                        "Default uncaught handler: thread " + thread.getName()
                                + " (id=" + thread.threadId() + ")",
                        error));
    }

    private static void awaitTasks(List<Future<?>> futures) {
        for (Future<?> future : futures) {
            try {
                future.get(DemoRuntime.SHUTDOWN_TIMEOUT.toSeconds() + 60, TimeUnit.SECONDS);
            } catch (InterruptedException e) {
                Thread.currentThread().interrupt();
                LOGGER.log(Level.WARNING, "Main thread interrupted while waiting for tasks", e);
                return;
            } catch (Exception e) {
                LOGGER.log(Level.WARNING, "Task completed with error; demo continues", e);
            }
        }
    }

    private static void shutdownExecutor(ExecutorService executor, Duration timeout) {
        executor.shutdown();
        try {
            if (!executor.awaitTermination(timeout.toMillis(), TimeUnit.MILLISECONDS)) {
                LOGGER.warning("Executor did not terminate in time; forcing shutdown");
                executor.shutdownNow();
                if (!executor.awaitTermination(timeout.toMillis(), TimeUnit.MILLISECONDS)) {
                    LOGGER.severe("Executor did not terminate after forced shutdown");
                }
            }
        } catch (InterruptedException e) {
            Thread.currentThread().interrupt();
            executor.shutdownNow();
            LOGGER.log(Level.WARNING, "Interrupted during executor shutdown", e);
        }
    }

    private static void logStats(DemoRuntime runtime, BlockingQueue<DataItem> queue) {
        LOGGER.info(() -> String.format(
                "[STATS] produced=%d consumed=%d queueSize=%d producerErrors=%d consumerErrors=%d active=%s",
                runtime.producedCount.get(),
                runtime.consumedCount.get(),
                queue.size(),
                runtime.producerErrorCount.get(),
                runtime.consumerErrorCount.get(),
                runtime.isActive()));
    }

    private static void logFinalSummary(DemoRuntime runtime, BlockingQueue<DataItem> queue, long startNanos) {
        long durationMs = TimeUnit.NANOSECONDS.toMillis(System.nanoTime() - startNanos);
        LOGGER.info(() -> String.format(
                "[SUMMARY] durationMs=%d produced=%d consumed=%d remainingInQueue=%d producerErrors=%d consumerErrors=%d",
                durationMs,
                runtime.producedCount.get(),
                runtime.consumedCount.get(),
                queue.size(),
                runtime.producerErrorCount.get(),
                runtime.consumerErrorCount.get()));
    }

    private static void configureLogging() {
        Logger rootLogger = Logger.getLogger("");
        for (var handler : rootLogger.getHandlers()) {
            rootLogger.removeHandler(handler);
        }

        ConsoleHandler handler = new ConsoleHandler();
        handler.setLevel(Level.INFO);
        handler.setFormatter(new Formatter() {
            @Override
            public String format(LogRecord record) {
                return String.format(
                        "%s [%s] %s%n",
                        Instant.ofEpochMilli(record.getMillis()),
                        Thread.currentThread().getName(),
                        formatMessage(record));
            }
        });

        rootLogger.addHandler(handler);
        rootLogger.setLevel(Level.INFO);
    }
}
