"""Program 28: Find the Factors of a Number

Finds and displays all factors (divisors) of a given integer.

Reference: https://www.programiz.com/python-programming/examples/factor-number
"""


def find_factors(n: int) -> list[int]:
    """Return a sorted list of all positive factors of n.

    Args:
        n: A positive integer.

    Returns:
        A sorted list of factors.
    """
    n = abs(n)
    if n == 0:
        return []
    factors = []
    for i in range(1, n + 1):
        if n % i == 0:
            factors.append(i)
    return factors


def main() -> None:
    """Read a number and display its factors."""
    num = int(input("Enter a positive integer: "))

    factors = find_factors(num)
    print(f"The factors of {num} are: {factors}")


if __name__ == "__main__":
    main()
