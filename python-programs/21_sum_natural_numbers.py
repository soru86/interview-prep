"""Program 21: Find the Sum of Natural Numbers

Computes the sum 1 + 2 + 3 + ... + n using both a loop and the formula n*(n+1)/2.

Reference: https://www.programiz.com/python-programming/examples/sum-natural-number
"""


def sum_natural_loop(n: int) -> int:
    """Compute sum of first n natural numbers using a loop."""
    if n < 1:
        return 0
    total = 0
    for i in range(1, n + 1):
        total += i
    return total


def sum_natural_formula(n: int) -> int:
    """Compute sum of first n natural numbers using the Gauss formula."""
    if n < 1:
        return 0
    return n * (n + 1) // 2


def main() -> None:
    """Read n and display the sum of first n natural numbers."""
    num = int(input("Enter a positive integer: "))

    if num < 1:
        print("Please enter a positive integer.")
    else:
        result = sum_natural_formula(num)
        print(f"The sum of first {num} natural numbers is {result}")


if __name__ == "__main__":
    main()
