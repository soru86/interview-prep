"""Program 56: Catch Multiple Exceptions in One Line

Demonstrates catching multiple exception types in a single except block.

Reference: https://www.programiz.com/python-programming/examples/catch-multiple-exceptions
"""


def divide(a: float, b: float) -> float:
    """Divide a by b."""
    return a / b


def main() -> None:
    """Demonstrate catching multiple exceptions."""
    test_cases = [
        ("10", "2"),
        ("10", "0"),
        ("abc", "2"),
        ("10", "xyz"),
    ]

    for a_str, b_str in test_cases:
        try:
            a = float(a_str)
            b = float(b_str)
            result = divide(a, b)
            print(f"  {a_str} / {b_str} = {result}")
        except (ValueError, ZeroDivisionError, TypeError) as e:
            print(f"  {a_str} / {b_str} -> Error: {type(e).__name__}: {e}")

    print("\n--- Another approach: separate handling ---")
    try:
        value = int("not_a_number")
    except (ValueError, TypeError) as e:
        print(f"  Caught {type(e).__name__}: {e}")


if __name__ == "__main__":
    main()
