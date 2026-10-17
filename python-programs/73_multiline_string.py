"""Program 73: Create a Long Multiline String

Demonstrates different ways to create multiline strings in Python.

Reference: https://www.programiz.com/python-programming/examples/multiline-string
"""


def main() -> None:
    """Demonstrate creating multiline strings."""
    # Method 1: Triple quotes (recommended)
    multiline_1 = """This is a
multiline string using
triple double quotes."""
    print("Method 1 — Triple double quotes:")
    print(multiline_1)

    print()

    # Method 2: Triple single quotes
    multiline_2 = '''This is a
multiline string using
triple single quotes.'''
    print("Method 2 — Triple single quotes:")
    print(multiline_2)

    print()

    # Method 3: Using backslash for line continuation
    multiline_3 = "This is a " \
                  "multiline string using " \
                  "backslash continuation."
    print("Method 3 — Backslash continuation (single line result):")
    print(multiline_3)

    print()

    # Method 4: Using parentheses for implicit continuation
    multiline_4 = (
        "This is a "
        "multiline string using "
        "parentheses."
    )
    print("Method 4 — Parentheses (single line result):")
    print(multiline_4)

    print()

    # Method 5: Using join with newlines
    multiline_5 = "\n".join([
        "This is a",
        "multiline string using",
        "join with newlines.",
    ])
    print("Method 5 — join():")
    print(multiline_5)


if __name__ == "__main__":
    main()
