"""Program 88: Check the File Size

Demonstrates checking the size of a file in bytes and human-readable format.

Reference: https://www.programiz.com/python-programming/examples/check-filesize
"""

import os
from pathlib import Path


def get_file_size(filepath: str) -> int:
    """Return the size of a file in bytes."""
    return os.path.getsize(filepath)


def format_file_size(size_bytes: int) -> str:
    """Convert bytes to a human-readable string."""
    for unit in ("B", "KB", "MB", "GB", "TB"):
        if size_bytes < 1024:
            return f"{size_bytes:.2f} {unit}"
        size_bytes /= 1024
    return f"{size_bytes:.2f} PB"


def main() -> None:
    """Display the size of a file."""
    # Use this script file itself
    filepath = __file__

    # Method 1: os.path.getsize()
    size = get_file_size(filepath)
    print(f"File: {os.path.basename(filepath)}")
    print(f"  os.path.getsize(): {size} bytes ({format_file_size(size)})")

    # Method 2: os.stat()
    stat_size = os.stat(filepath).st_size
    print(f"  os.stat().st_size: {stat_size} bytes")

    # Method 3: pathlib
    path_size = Path(filepath).stat().st_size
    print(f"  pathlib stat:      {path_size} bytes")

    # Example with different sizes
    print("\n--- Size Format Examples ---")
    for size in [500, 1536, 1_048_576, 1_500_000_000]:
        print(f"  {size:>15,} bytes = {format_file_size(size)}")


if __name__ == "__main__":
    main()
