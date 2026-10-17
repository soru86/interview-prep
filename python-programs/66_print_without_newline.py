"""Program 66: Print Output Without a Newline

Demonstrates printing on the same line using the end parameter.

Reference: https://www.programiz.com/python-programming/examples/print-without-newline
"""

import sys


def main() -> None:
    """Demonstrate printing without a newline."""
    # Method 1: Using end parameter (recommended)
    print("Method 1 — Using end parameter:")
    print("Hello", end=" ")
    print("World", end="!")
    print()  # Move to next line

    # Method 2: Using end with different separator
    print("\nMethod 2 — Custom separators:")
    for i in range(1, 6):
        print(i, end=" -> " if i < 5 else "\n")

    # Method 3: Using sep parameter
    print("\nMethod 3 — Using sep parameter:")
    print("apple", "banana", "cherry", sep=", ")
    print(2024, 3, 15, sep="-")

    # Method 4: Using sys.stdout.write
    print("\nMethod 4 — Using sys.stdout.write:")
    sys.stdout.write("Hello ")
    sys.stdout.write("World!\n")


if __name__ == "__main__":
    main()
