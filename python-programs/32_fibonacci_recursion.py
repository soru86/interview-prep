"""Program 32: Display Fibonacci Sequence Using Recursion

Generates Fibonacci numbers using a recursive approach.

Reference: https://www.programiz.com/python-programming/examples/fibonacci-recursion
"""


def fibonacci_recursive(n: int) -> int:
    """Return the nth Fibonacci number using recursion.

    Args:
        n: The index (0-based) of the Fibonacci number to compute.

    Returns:
        The nth Fibonacci number.
    """
    if n <= 0:
        return 0
    if n == 1:
        return 1
    return fibonacci_recursive(n - 1) + fibonacci_recursive(n - 2)


def main() -> None:
    """Read the number of terms and display the Fibonacci sequence."""
    n_terms = int(input("How many Fibonacci terms to display? "))

    if n_terms <= 0:
        print("Please enter a positive integer.")
        return

    print(f"\nFibonacci sequence ({n_terms} terms) using recursion:")
    sequence = [fibonacci_recursive(i) for i in range(n_terms)]
    print(", ".join(map(str, sequence)))


if __name__ == "__main__":
    main()
