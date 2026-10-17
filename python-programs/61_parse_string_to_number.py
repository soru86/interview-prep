"""Program 61: Parse a String to a Float or Int

Demonstrates converting strings to numeric types safely.

Reference: https://www.programiz.com/python-programming/examples/string-to-float-or-int
"""


def parse_to_number(value: str) -> int | float | None:
    """Parse a string to int or float. Returns None if parsing fails."""
    try:
        # Try int first
        return int(value)
    except ValueError:
        try:
            return float(value)
        except ValueError:
            return None


def main() -> None:
    """Demonstrate parsing strings to numbers."""
    test_values = ["42", "3.14", "-17", "1e5", "0xFF", "hello", ""]

    print("String to Number Parsing:")
    print("-" * 40)
    for val in test_values:
        result = parse_to_number(val)
        if result is not None:
            print(f"  '{val}' -> {result} (type: {type(result).__name__})")
        else:
            print(f"  '{val}' -> Cannot parse")

    # Direct conversions
    print(f"\nint('10'):      {int('10')}")
    print(f"float('10.5'):  {float('10.5')}")
    print(f"int(10.9):      {int(10.9)}")    # Truncates
    print(f"float(10):      {float(10)}")


if __name__ == "__main__":
    main()
