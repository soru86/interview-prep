"""Program 71: Append to a File

Demonstrates appending content to an existing file.

Reference: https://www.programiz.com/python-programming/examples/append-to-file
"""

import tempfile
import os


def append_to_file(filepath: str, content: str) -> None:
    """Append content to a file."""
    with open(filepath, "a") as f:
        f.write(content)


def main() -> None:
    """Demonstrate appending to a file."""
    # Create a temporary file
    with tempfile.NamedTemporaryFile(mode="w", suffix=".txt", delete=False) as tmp:
        tmp.write("Line 1: Original content\n")
        tmp.write("Line 2: More original content\n")
        filepath = tmp.name

    try:
        print("--- Before appending ---")
        with open(filepath) as f:
            print(f.read())

        # Append new content
        append_to_file(filepath, "Line 3: Appended content\n")
        append_to_file(filepath, "Line 4: Another appended line\n")

        print("--- After appending ---")
        with open(filepath) as f:
            print(f.read())
    finally:
        os.remove(filepath)


if __name__ == "__main__":
    main()
