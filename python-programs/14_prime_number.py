"""Program 14: Check Prime Number

Determines whether a given number is a prime number.
A prime number is greater than 1 and has no positive divisors other than 1 and itself.

Reference: https://www.programiz.com/python-programming/examples/prime-number
"""

import math


def is_prime(n: int) -> bool:
    """Return True if n is a prime number, False otherwise.

    Uses trial division up to sqrt(n) for efficiency.
    """
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


def main() -> None:
    """Read a number and check if it is prime."""
    num = int(input("Enter a number: "))

    if is_prime(num):
        print(f"{num} is a prime number")
    else:
        print(f"{num} is not a prime number")


if __name__ == "__main__":
    main()
