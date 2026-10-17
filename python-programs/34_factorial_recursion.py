"""Program 34: Find Factorial of Number Using Recursion

Computes n! using a recursive approach.

Reference: https://www.programiz.com/python-programming/examples/factorial-recursion
"""


def factorial_recursive(n: int) -> int:
    """Compute the factorial of n using recursion.

    Args:
        n: A non-negative integer.

    Returns:
        The factorial of n.

    Raises:
        ValueError: If n is negative.
    """
    if n < 0:
        raise ValueError("Factorial is not defined for negative numbers")
    if n in (0, 1):
        return 1
    return n * factorial_recursive(n - 1)


def main() -> None:
    """Read a number and display its factorial using recursion."""
    num = int(input("Enter a non-negative integer: "))

    try:
        result = factorial_recursive(num)
        print(f"The factorial of {num} is {result}")
    except ValueError as e:
        print(f"Error: {e}")


if __name__ == "__main__":
    main()
