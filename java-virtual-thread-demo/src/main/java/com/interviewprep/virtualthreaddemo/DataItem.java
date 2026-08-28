package com.interviewprep.virtualthreaddemo;

import java.time.Instant;

public record DataItem(long sequenceId, int producerId, String payload, Instant createdAt) {
}
