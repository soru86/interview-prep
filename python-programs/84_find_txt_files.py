"""Program 84: Find All Files with .txt Extension Present Inside a Directory

Demonstrates finding files with a specific extension in a directory.

Reference: https://www.programiz.com/python-programming/examples/find-txt-files
"""

import os
import glob
from pathlib import Path


def find_txt_files_os(directory: str) -> list[str]:
    """Find .txt files using os.listdir()."""
    return [f for f in os.listdir(directory) if f.endswith(".txt")]


def find_txt_files_glob(directory: str) -> list[str]:
    """Find .txt files using glob."""
    pattern = os.path.join(directory, "*.txt")
    return [os.path.basename(f) for f in glob.glob(pattern)]


def find_txt_files_pathlib(directory: str) -> list[str]:
    """Find .txt files using pathlib."""
    return [f.name for f in Path(directory).glob("*.txt")]


def main() -> None:
    """Demonstrate finding .txt files in a directory."""
    # Use current directory as the search path
    search_dir = os.getcwd()

    print(f"Searching in: {search_dir}\n")

    # Method 1: os.listdir
    txt_files = find_txt_files_os(search_dir)
    print(f"Method 1 (os.listdir): {txt_files}")

    # Method 2: glob
    txt_files_glob = find_txt_files_glob(search_dir)
    print(f"Method 2 (glob):       {txt_files_glob}")

    # Method 3: pathlib
    txt_files_pathlib = find_txt_files_pathlib(search_dir)
    print(f"Method 3 (pathlib):    {txt_files_pathlib}")

    # Recursive search with rglob
    print("\nRecursive search (pathlib rglob):")
    for txt_file in Path(search_dir).rglob("*.txt"):
        print(f"  {txt_file.relative_to(search_dir)}")


if __name__ == "__main__":
    main()
