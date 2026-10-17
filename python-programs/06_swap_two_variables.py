"""Program 6: Swap Two Variables

Demonstrates multiple ways to swap two variables in Python.

Reference: https://www.programiz.com/python-programming/examples/swap-variables
"""


def swap_with_temp(a, b):
    """Swap two values using a temporary variable."""
    temp = a
    a = b
    b = temp
    return a, b


def swap_pythonic(a, b):
    """Swap two values using Python's tuple unpacking (idiomatic)."""
    a, b = b, a
    return a, b


def swap_with_arithmetic(a: float, b: float):
    """Swap two numeric values using arithmetic (no extra variable)."""
    a = a + b
    b = a - b
    a = a - b
    return a, b


def main() -> None:
    """Demonstrate different swapping techniques."""
    x = float(input("Enter value of x: "))
    y = float(input("Enter value of y: "))

    print(f"\nBefore swap: x = {x}, y = {y}")

    # Method 1: Pythonic swap (recommended)
    x, y = swap_pythonic(x, y)
    print(f"After swap:  x = {x}, y = {y}")


if __name__ == "__main__":
    main()
