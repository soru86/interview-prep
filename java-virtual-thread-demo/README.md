# Java Virtual Thread Demo

A Java 21 demonstration of a high-scale **producer–consumer** pipeline using a fixed pool of **20,000 virtual threads** — 10,000 producers and 10,000 consumers running continuously for **15 minutes**.

## Features

- Fixed virtual-thread pool (`20,000` threads)
- Continuous producer stream into a bounded `ArrayBlockingQueue`
- Continuous consumer processing with resilient error recovery
- Per-event console logging with virtual thread id and consumed data
- Periodic stats every 30 seconds
- Graceful shutdown after the configured duration

## Requirements

- Java 21+
- Maven 3.8+

## Project layout

```
src/main/java/com/interviewprep/virtualthreaddemo/
├── VirtualThreadDemo.java   # entry point and orchestration
├── ProducerTask.java        # continuous producer loop
├── ConsumerTask.java        # continuous consumer loop
├── DataItem.java            # shared data record
└── DemoRuntime.java         # shared runtime state and constants
```

## Run

Default (15 minutes):

```bash
cd java-virtual-thread-demo
mvn -q compile exec:java
```

Short local smoke test (30 seconds):

```bash
mvn -q compile exec:java -Ddemo.duration.seconds=30
```

Custom duration in minutes:

```bash
mvn -q compile exec:java -Ddemo.duration.minutes=5
```

## Sample log output

```
2026-06-09T12:00:01.123456789Z [main] Starting virtual-thread demo | poolSize=20000 producers=10000 consumers=10000 ...
2026-06-09T12:00:01.234567890Z [vt-42] [PRODUCER] threadId=42 threadName=vt-42 producerId=7 data=DataItem[...] queueSize=128
2026-06-09T12:00:01.245678901Z [vt-108] [CONSUMER] threadId=108 threadName=vt-108 consumerId=3 data=DataItem[...] queueSize=127
2026-06-09T12:00:31.000000000Z [demo-scheduler] [STATS] produced=1250000 consumed=1249800 queueSize=200 ...
```

## Error handling

- Each producer/consumer loop catches exceptions, logs them, and continues
- Virtual-thread factory and default uncaught-exception handlers log unexpected failures
- `InterruptedException` restores the interrupt flag and exits the task cleanly
- Top-level `main` uses `try/finally` to stop workers and print a final summary

## Notes

- Logging every produced/consumed item for a full 15-minute run generates very high console volume. Use `-Ddemo.duration.seconds=30` for quick validation.
- Queue capacity is `20,000`; producers block when the queue is full, which naturally back-pressures the pipeline.
