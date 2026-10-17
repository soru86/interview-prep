"""Program 75: Measure the Elapsed Time in Python

Demonstrates measuring code execution time using time and timeit.

Reference: https://www.programiz.com/python-programming/examples/elapsed-time
"""

import time
import timeit


def slow_function() -> int:
    """A deliberately slow function for timing demonstration."""
    total = 0
    for i in range(1_000_000):
        total += i
    return total


def main() -> None:
    """Demonstrate measuring elapsed time."""
    # Method 1: Using time.time()
    start = time.time()
    slow_function()
    end = time.time()
    print(f"Method 1 — time.time():       {end - start:.6f} seconds")

    # Method 2: Using time.perf_counter() — higher resolution
    start = time.perf_counter()
    slow_function()
    end = time.perf_counter()
    print(f"Method 2 — time.perf_counter(): {end - start:.6f} seconds")

    # Method 3: Using time.process_time() — CPU time only
    start = time.process_time()
    slow_function()
    end = time.process_time()
    print(f"Method 3 — time.process_time(): {end - start:.6f} seconds")

    # Method 4: Using timeit for benchmarking
    elapsed = timeit.timeit("sum(range(1000))", number=10000)
    print(f"Method 4 — timeit (10000 runs): {elapsed:.6f} seconds")


if __name__ == "__main__":
    main()
