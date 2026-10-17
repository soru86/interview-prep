"""Program 19: Check Armstrong Number

An Armstrong (narcissistic) number is a number that equals the sum of its
digits each raised to the power of the number of digits.
Example: 153 = 1³ + 5³ + 3³

Reference: https://www.programiz.com/python-programming/examples/armstrong-number
"""


def is_armstrong(num: int) -> bool:
    """Return True if num is an Armstrong number.

    Args:
        num: A non-negative integer to check.

    Returns:
        True if the number is an Armstrong number.
    """
    digits = str(abs(num))
    power = len(digits)
    total = sum(int(d) ** power for d in digits)
    return total == num


def main() -> None:
    """Read a number and check if it is an Armstrong number."""
    num = int(input("Enter a number: "))

    if is_armstrong(num):
        print(f"{num} is an Armstrong number")
    else:
        print(f"{num} is not an Armstrong number")


if __name__ == "__main__":
    main()
