package com.interviewprep.producerconsumer;

import com.interviewprep.producerconsumer.config.DemoConfig;
import com.interviewprep.producerconsumer.executor.ProducerConsumerExecutorDemo;
import com.interviewprep.producerconsumer.support.DemoResult;
import com.interviewprep.producerconsumer.virtualthread.ProducerConsumerVirtualThreadDemo;

import java.util.logging.Level;
import java.util.logging.Logger;

public final class Main {

    private static final Logger LOGGER = Logger.getLogger(Main.class.getName());

    private Main() {
    }

    public static void main(String[] args) {
        String mode = args.length > 0 ? args[0].toLowerCase() : "executor";
        DemoConfig config = DemoConfig.DEFAULT;

        try {
            DemoResult result = switch (mode) {
                case "executor" -> new ProducerConsumerExecutorDemo(config).run();
                case "virtual" -> new ProducerConsumerVirtualThreadDemo(config).run();
                default -> throw new IllegalArgumentException(
                        "Unknown mode: " + mode + ". Use 'executor' or 'virtual'.");
            };

            result.printSummary();
            if (!result.success()) {
                System.exit(1);
            }
        } catch (InterruptedException e) {
            Thread.currentThread().interrupt();
            LOGGER.log(Level.SEVERE, "Demo interrupted", e);
            System.exit(1);
        } catch (Exception e) {
            LOGGER.log(Level.SEVERE, "Demo failed", e);
            System.exit(1);
        }
    }
}
