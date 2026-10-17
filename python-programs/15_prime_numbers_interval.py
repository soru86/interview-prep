"""Program 15: Print All Prime Numbers in an Interval

Finds and prints all prime numbers within a given range [lower, upper].

Reference: https://www.programiz.com/python-programming/examples/prime-number-intervals
"""

import math


def is_prime(n: int) -> bool:
    """Return True if n is a prime number."""
    if n < 2:
        return False
    if n < 4:
        return True
    if n % 2 == 0 or n % 3 == 0:
        return False
    for i in range(5, int(math.isqrt(n)) + 1, 2):
        if n % i == 0:
            return False
    return True


def primes_in_interval(lower: int, upper: int) -> list[int]:
    """Return a list of all prime numbers in the interval [lower, upper]."""
    return [n for n in range(lower, upper + 1) if is_prime(n)]


def main() -> None:
    """Read an interval and display all prime numbers within it."""
    lower = int(input("Enter lower bound: "))
    upper = int(input("Enter upper bound: "))

    primes = primes_in_interval(lower, upper)

    print(f"\nPrime numbers between {lower} and {upper}:")
    if primes:
        print(", ".join(map(str, primes)))
    else:
        print("No prime numbers found in this interval.")


if __name__ == "__main__":
    main()
