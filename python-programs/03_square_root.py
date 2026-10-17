"""Program 3: Find the Square Root

Demonstrates computing the square root of a number using the ** operator
and the math module.

Reference: https://www.programiz.com/python-programming/examples/square-root
"""

import math


def square_root(number: float) -> float:
    """Return the square root of a non-negative number."""
    if number < 0:
        raise ValueError("Cannot compute square root of a negative number")
    return math.sqrt(number)


def main() -> None:
    """Read a number and display its square root."""
    num = float(input("Enter a number: "))

    # Method 1: Using ** operator
    sqrt_operator = num ** 0.5
    print(f"Square root of {num} (using ** operator): {sqrt_operator:.4f}")

    # Method 2: Using math.sqrt()
    sqrt_math = square_root(num)
    print(f"Square root of {num} (using math.sqrt):   {sqrt_math:.4f}")


if __name__ == "__main__":
    main()
