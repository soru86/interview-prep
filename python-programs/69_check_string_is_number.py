"""Program 69: Check If a String Is a Number (Float)

Demonstrates checking if a string can be converted to a float.

Reference: https://www.programiz.com/python-programming/examples/check-string-number
"""


def is_number(value: str) -> bool:
    """Return True if the string represents a valid float or int."""
    try:
        float(value)
        return True
    except ValueError:
        return False


def main() -> None:
    """Demonstrate checking if strings are numbers."""
    test_values = ["123", "3.14", "-42", "1e10", "0.001",
                   "hello", "", "12.3.4", "NaN", "inf", "1+2j"]

    print("Is the string a number?")
    print("-" * 35)
    for val in test_values:
        result = is_number(val)
        print(f"  '{val:10s}' -> {result}")


if __name__ == "__main__":
    main()
