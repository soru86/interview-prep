"""Program 16: Find the Factorial of a Number

Computes n! using both iterative and math.factorial approaches.
n! = 1 × 2 × 3 × ... × n (0! = 1 by convention).

Reference: https://www.programiz.com/python-programming/examples/factorial
"""

import math


def factorial_iterative(n: int) -> int:
    """Compute factorial iteratively.

    Args:
        n: A non-negative integer.

    Returns:
        The factorial of n.

    Raises:
        ValueError: If n is negative.
    """
    if n < 0:
        raise ValueError("Factorial is not defined for negative numbers")

    result = 1
    for i in range(2, n + 1):
        result *= i
    return result


def main() -> None:
    """Read a number and display its factorial."""
    num = int(input("Enter a non-negative integer: "))

    result = factorial_iterative(num)
    print(f"The factorial of {num} is {result}")

    # Verification with math.factorial
    assert result == math.factorial(num)


if __name__ == "__main__":
    main()
