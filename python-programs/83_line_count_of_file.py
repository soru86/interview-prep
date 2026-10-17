"""Program 83: Get Line Count of a File

Demonstrates counting the number of lines in a file.

Reference: https://www.programiz.com/python-programming/examples/line-count
"""

import tempfile
import os


def count_lines(filepath: str) -> int:
    """Count the number of lines in a file."""
    with open(filepath, "r") as f:
        return sum(1 for _ in f)


def count_lines_readlines(filepath: str) -> int:
    """Count lines using readlines()."""
    with open(filepath, "r") as f:
        return len(f.readlines())


def main() -> None:
    """Demonstrate counting lines in a file."""
    # Create a temporary file
    with tempfile.NamedTemporaryFile(mode="w", suffix=".txt", delete=False) as tmp:
        lines = [
            "First line\n",
            "Second line\n",
            "Third line\n",
            "Fourth line\n",
            "Fifth line\n",
        ]
        tmp.writelines(lines)
        filepath = tmp.name

    try:
        count1 = count_lines(filepath)
        count2 = count_lines_readlines(filepath)

        print(f"File: {os.path.basename(filepath)}")
        print(f"Line count (generator): {count1}")
        print(f"Line count (readlines): {count2}")
    finally:
        os.remove(filepath)


if __name__ == "__main__":
    main()
