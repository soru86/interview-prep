"""Program 11: Check if a Number is Odd or Even

Demonstrates using the modulo operator to determine parity.

Reference: https://www.programiz.com/python-programming/examples/odd-even
"""


def is_even(number: int) -> bool:
    """Return True if the number is even, False otherwise."""
    return number % 2 == 0


def main() -> None:
    """Read a number and check if it is odd or even."""
    num = int(input("Enter a number: "))

    if is_even(num):
        print(f"{num} is even")
    else:
        print(f"{num} is odd")


if __name__ == "__main__":
    main()
