"""Program 13: Find the Largest Among Three Numbers

Demonstrates finding the maximum of three numbers using conditionals
and Python's built-in max().

Reference: https://www.programiz.com/python-programming/examples/largest-number-three
"""


def largest_of_three(a: float, b: float, c: float) -> float:
    """Return the largest of three numbers using conditionals."""
    if a >= b and a >= c:
        return a
    elif b >= a and b >= c:
        return b
    else:
        return c


def main() -> None:
    """Read three numbers and display the largest."""
    num1 = float(input("Enter first number: "))
    num2 = float(input("Enter second number: "))
    num3 = float(input("Enter third number: "))

    # Method 1: Using conditionals
    result = largest_of_three(num1, num2, num3)
    print(f"The largest number is {result}")

    # Method 2: Using built-in max()
    print(f"Verification with max(): {max(num1, num2, num3)}")


if __name__ == "__main__":
    main()
