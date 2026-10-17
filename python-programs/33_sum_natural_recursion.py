"""Program 33: Find Sum of Natural Numbers Using Recursion

Computes the sum 1 + 2 + ... + n using a recursive approach.

Reference: https://www.programiz.com/python-programming/examples/natural-number-recursion
"""


def sum_natural_recursive(n: int) -> int:
    """Compute the sum of first n natural numbers using recursion.

    Args:
        n: A positive integer.

    Returns:
        The sum of 1 + 2 + ... + n.
    """
    if n <= 0:
        return 0
    return n + sum_natural_recursive(n - 1)


def main() -> None:
    """Read a number and display the sum of natural numbers up to it."""
    num = int(input("Enter a positive integer: "))

    if num < 1:
        print("Please enter a positive integer.")
    else:
        result = sum_natural_recursive(num)
        print(f"The sum of first {num} natural numbers is {result}")


if __name__ == "__main__":
    main()
