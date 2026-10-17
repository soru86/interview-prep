"""Program 49: Safely Create a Nested Directory

Demonstrates creating nested directories safely using os.makedirs() and pathlib.

Reference: https://www.programiz.com/python-programming/examples/create-nested-directories
"""

import os
from pathlib import Path


def create_nested_dir_os(path: str) -> None:
    """Create nested directories using os.makedirs (won't error if exists)."""
    os.makedirs(path, exist_ok=True)
    print(f"Created directory (os.makedirs): {path}")


def create_nested_dir_pathlib(path: str) -> None:
    """Create nested directories using pathlib.Path.mkdir."""
    Path(path).mkdir(parents=True, exist_ok=True)
    print(f"Created directory (pathlib):     {path}")


def main() -> None:
    """Demonstrate safely creating nested directories."""
    # Method 1: Using os.makedirs
    dir_path_1 = os.path.join("test_directory", "level1", "level2")
    create_nested_dir_os(dir_path_1)

    # Method 2: Using pathlib
    dir_path_2 = os.path.join("test_directory", "another", "nested", "dir")
    create_nested_dir_pathlib(dir_path_2)

    # Verify they exist
    print(f"\n'{dir_path_1}' exists: {os.path.isdir(dir_path_1)}")
    print(f"'{dir_path_2}' exists: {os.path.isdir(dir_path_2)}")

    # Clean up
    import shutil
    shutil.rmtree("test_directory", ignore_errors=True)
    print("\nCleaned up test directories.")


if __name__ == "__main__":
    main()
