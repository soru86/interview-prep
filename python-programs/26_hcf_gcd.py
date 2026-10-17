"""Program 26: Find HCF or GCD

Computes the Highest Common Factor (HCF) / Greatest Common Divisor (GCD)
of two numbers using the Euclidean algorithm and math.gcd().

Reference: https://www.programiz.com/python-programming/examples/hcf
"""

import math


def gcd_euclidean(a: int, b: int) -> int:
    """Compute GCD using the Euclidean algorithm."""
    a, b = abs(a), abs(b)
    while b:
        a, b = b, a % b
    return a


def main() -> None:
    """Read two numbers and display their HCF/GCD."""
    num1 = int(input("Enter first number: "))
    num2 = int(input("Enter second number: "))

    # Method 1: Euclidean algorithm
    result = gcd_euclidean(num1, num2)
    print(f"The HCF/GCD of {num1} and {num2} is {result}")

    # Method 2: Using math.gcd (verification)
    assert result == math.gcd(num1, num2)


if __name__ == "__main__":
    main()
