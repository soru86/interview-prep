# Producer-Consumer Demo

A Java 21 demonstration of the classic **producer-consumer problem** with two implementations:

1. **Executor framework** — fixed-size platform thread pool with non-blocking buffer operations and task re-scheduling
2. **Virtual threads** — one virtual thread per producer/consumer with blocking queue operations

## Problem

Multiple producers generate items and multiple consumers process them through a **bounded buffer**. Producers must wait when the buffer is full; consumers must wait when it is empty.

## Why two implementations?

### Fixed thread pool deadlock risk

If producer and consumer tasks share a **small fixed thread pool** and use blocking `put()` / `take()`, all pool threads can block waiting on a full or empty buffer with no runnable left to make progress — a **pool deadlock**.

**Executor demo solution:** use timed `offer()` / `poll()` and **re-submit** the task to the executor when the buffer is full or empty. The platform thread returns to the pool immediately instead of blocking indefinitely.

**Virtual-thread demo solution:** blocking `put()` / `take()` is safe because blocking a virtual thread does not pin a platform (carrier) thread. Each producer and consumer runs on its own virtual thread via `Executors.newVirtualThreadPerTaskExecutor()`.

## Project structure

```
src/main/java/com/interviewprep/producerconsumer/
├── Main.java
├── config/DemoConfig.java
├── model/WorkItem.java
├── buffer/BoundedBuffer.java
├── support/DemoResult.java, ShutdownSupport.java
├── executor/          # Fixed pool + non-blocking reschedule
└── virtualthread/     # Virtual threads + blocking ops
```

## Requirements

- Java 21+
- Maven 3.8+

## Build

```bash
cd producer-consumer-demo
mvn -q compile
```

## Run

**Executor demo (default):**

```bash
mvn -q exec:java -Dexec.args=executor
```

**Virtual-thread demo:**

```bash
mvn -q exec:java -Dexec.args=virtual
```

## Default configuration

| Parameter | Value |
|-----------|-------|
| Pool size | 4 |
| Buffer capacity | 5 |
| Producers | 3 |
| Consumers | 3 |
| Items per producer | 10 |
| Total items | 30 |

## Expected output

Both demos produce and consume all 30 items and print a summary:

```
=== Executor Demo Complete ===
Produced: 30, Consumed: 30, Expected: 30, Duration: 142ms
Pool size: 4, Buffer: 5, Producers: 3, Consumers: 3
```

## Error handling

- Invalid configuration throws `IllegalArgumentException` at startup
- Task failures are captured, logged, and trigger executor shutdown
- `InterruptedException` restores the interrupt flag and exits cleanly
- Completion is verified: produced and consumed counts must match the expected total
