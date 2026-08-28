package com.interviewprep.producerconsumer.support;

import java.time.Duration;
import java.util.concurrent.ExecutorService;
import java.util.concurrent.TimeUnit;
import java.util.logging.Level;
import java.util.logging.Logger;

public final class ShutdownSupport {

    private static final Logger LOGGER = Logger.getLogger(ShutdownSupport.class.getName());

    private ShutdownSupport() {
    }

    public static void gracefulShutdown(ExecutorService executor, Duration timeout) throws InterruptedException {
        executor.shutdown();
        if (!executor.awaitTermination(timeout.toMillis(), TimeUnit.MILLISECONDS)) {
            LOGGER.warning("Executor did not terminate in time, forcing shutdown");
            executor.shutdownNow();
            if (!executor.awaitTermination(timeout.toMillis(), TimeUnit.MILLISECONDS)) {
                LOGGER.severe("Executor did not terminate after forced shutdown");
            }
        }
    }
}
