"""Program 29: Make a Simple Calculator

Implements a simple calculator that performs basic arithmetic operations
(+, -, *, /) based on user input.

Reference: https://www.programiz.com/python-programming/examples/calculator
"""


def add(a: float, b: float) -> float:
    """Return the sum of a and b."""
    return a + b


def subtract(a: float, b: float) -> float:
    """Return the difference of a and b."""
    return a - b


def multiply(a: float, b: float) -> float:
    """Return the product of a and b."""
    return a * b


def divide(a: float, b: float) -> float:
    """Return the quotient of a and b.

    Raises:
        ZeroDivisionError: If b is zero.
    """
    if b == 0:
        raise ZeroDivisionError("Cannot divide by zero")
    return a / b


def main() -> None:
    """Run a simple calculator."""
    print("Simple Calculator")
    print("-" * 30)
    print("Select operation:")
    print("  1. Add (+)")
    print("  2. Subtract (-)")
    print("  3. Multiply (*)")
    print("  4. Divide (/)")

    choice = input("\nEnter choice (1/2/3/4): ")

    if choice not in ("1", "2", "3", "4"):
        print("Invalid choice!")
        return

    num1 = float(input("Enter first number: "))
    num2 = float(input("Enter second number: "))

    operations = {
        "1": ("Addition", add),
        "2": ("Subtraction", subtract),
        "3": ("Multiplication", multiply),
        "4": ("Division", divide),
    }

    name, operation = operations[choice]

    try:
        result = operation(num1, num2)
        print(f"\n{name}: {num1} {'+' if choice == '1' else '-' if choice == '2' else '*' if choice == '3' else '/'} {num2} = {result}")
    except ZeroDivisionError as e:
        print(f"\nError: {e}")


if __name__ == "__main__":
    main()
