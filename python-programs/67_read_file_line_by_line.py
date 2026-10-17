"""Program 67: Read a File Line by Line Into a List

Demonstrates reading file contents line by line into a list.

Reference: https://www.programiz.com/python-programming/examples/read-line-by-line
"""

import tempfile
import os


def read_lines_readlines(filepath: str) -> list[str]:
    """Read all lines from a file using readlines()."""
    with open(filepath, "r") as f:
        return f.readlines()


def read_lines_iteration(filepath: str) -> list[str]:
    """Read lines from a file by iterating over the file object."""
    with open(filepath, "r") as f:
        return [line.rstrip("\n") for line in f]


def read_lines_splitlines(filepath: str) -> list[str]:
    """Read lines using read() + splitlines()."""
    with open(filepath, "r") as f:
        return f.read().splitlines()


def main() -> None:
    """Demonstrate reading a file line by line."""
    # Create a temporary file for demonstration
    with tempfile.NamedTemporaryFile(mode="w", suffix=".txt", delete=False) as tmp:
        tmp.write("Line 1: Hello\n")
        tmp.write("Line 2: World\n")
        tmp.write("Line 3: Python\n")
        tmp.write("Line 4: Programming\n")
        filepath = tmp.name

    try:
        # Method 1: readlines()
        lines1 = read_lines_readlines(filepath)
        print("Method 1 — readlines() (includes \\n):")
        for line in lines1:
            print(f"  {line!r}")

        # Method 2: Iteration with strip
        lines2 = read_lines_iteration(filepath)
        print("\nMethod 2 — Iteration (stripped):")
        for line in lines2:
            print(f"  '{line}'")

        # Method 3: splitlines()
        lines3 = read_lines_splitlines(filepath)
        print(f"\nMethod 3 — splitlines(): {lines3}")
    finally:
        os.remove(filepath)


if __name__ == "__main__":
    main()
