"""Program 2: Add Two Numbers

Demonstrates adding two numbers and displaying the result.

Reference: https://www.programiz.com/python-programming/examples/add-number
"""


def add_two_numbers(a: float, b: float) -> float:
    """Return the sum of two numbers."""
    return a + b


def main() -> None:
    """Read two numbers from the user and print their sum."""
    num1 = float(input("Enter first number: "))
    num2 = float(input("Enter second number: "))

    total = add_two_numbers(num1, num2)
    print(f"The sum of {num1} and {num2} is {total}")


if __name__ == "__main__":
    main()
