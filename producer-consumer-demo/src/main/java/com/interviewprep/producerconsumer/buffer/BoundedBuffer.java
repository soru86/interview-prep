package com.interviewprep.producerconsumer.buffer;

import java.time.Duration;
import java.util.Optional;
import java.util.concurrent.ArrayBlockingQueue;
import java.util.concurrent.BlockingQueue;
import java.util.concurrent.TimeUnit;
import java.util.logging.Level;
import java.util.logging.Logger;

public final class BoundedBuffer<T> {

    private static final Logger LOGGER = Logger.getLogger(BoundedBuffer.class.getName());

    private final BlockingQueue<T> queue;
    private final int capacity;

    public BoundedBuffer(int capacity) {
        if (capacity < 1) {
            throw new IllegalArgumentException("capacity must be at least 1, got: " + capacity);
        }
        this.capacity = capacity;
        this.queue = new ArrayBlockingQueue<>(capacity);
    }

    public boolean tryOffer(T item, Duration timeout) throws InterruptedException {
        boolean accepted = queue.offer(item, timeout.toMillis(), TimeUnit.MILLISECONDS);
        if (!accepted) {
            LOGGER.log(Level.FINE, "Buffer full ({0}/{1}), offer timed out", new Object[] {queue.size(), capacity});
        }
        return accepted;
    }

    public Optional<T> tryPoll(Duration timeout) throws InterruptedException {
        T item = queue.poll(timeout.toMillis(), TimeUnit.MILLISECONDS);
        if (item == null) {
            LOGGER.log(Level.FINE, "Buffer empty ({0}/{1}), poll timed out", new Object[] {queue.size(), capacity});
        }
        return Optional.ofNullable(item);
    }

    public void put(T item) throws InterruptedException {
        queue.put(item);
    }

    public T take() throws InterruptedException {
        return queue.take();
    }

    public int size() {
        return queue.size();
    }

    public int remainingCapacity() {
        return queue.remainingCapacity();
    }

    public int capacity() {
        return capacity;
    }
}
