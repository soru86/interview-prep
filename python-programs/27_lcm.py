"""Program 27: Find LCM

Computes the Least Common Multiple (LCM) of two numbers.
LCM(a, b) = |a * b| / GCD(a, b)

Reference: https://www.programiz.com/python-programming/examples/lcm
"""

import math


def compute_gcd(a: int, b: int) -> int:
    """Compute GCD using the Euclidean algorithm."""
    a, b = abs(a), abs(b)
    while b:
        a, b = b, a % b
    return a


def compute_lcm(a: int, b: int) -> int:
    """Compute LCM using the GCD relationship."""
    if a == 0 or b == 0:
        return 0
    return abs(a * b) // compute_gcd(a, b)


def main() -> None:
    """Read two numbers and display their LCM."""
    num1 = int(input("Enter first number: "))
    num2 = int(input("Enter second number: "))

    result = compute_lcm(num1, num2)
    print(f"The LCM of {num1} and {num2} is {result}")

    # Verification with math.lcm (Python 3.9+)
    assert result == math.lcm(num1, num2)


if __name__ == "__main__":
    main()
