package com.interviewprep.producerconsumer.model;

public record WorkItem(int producerId, int itemNumber) {

    public WorkItem {
        if (producerId < 0) {
            throw new IllegalArgumentException("producerId must be non-negative, got: " + producerId);
        }
        if (itemNumber < 0) {
            throw new IllegalArgumentException("itemNumber must be non-negative, got: " + itemNumber);
        }
    }

    @Override
    public String toString() {
        return "WorkItem{producer=" + producerId + ", item=" + itemNumber + '}';
    }
}
