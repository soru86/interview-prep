"""Program 74: Extract Extension From the File Name

Demonstrates extracting the file extension from a filename or path.

Reference: https://www.programiz.com/python-programming/examples/extract-file-extension
"""

import os
from pathlib import Path


def get_extension_os(filepath: str) -> str:
    """Extract the file extension using os.path.splitext."""
    _, ext = os.path.splitext(filepath)
    return ext


def get_extension_pathlib(filepath: str) -> str:
    """Extract the file extension using pathlib."""
    return Path(filepath).suffix


def main() -> None:
    """Demonstrate extracting file extensions."""
    filenames = [
        "document.pdf",
        "image.png",
        "archive.tar.gz",
        "/home/user/data.csv",
        "no_extension",
        ".hidden_file",
        "file.with.many.dots.txt",
    ]

    print(f"{'Filename':<30} {'os.path':>10} {'pathlib':>10}")
    print("-" * 52)

    for filename in filenames:
        ext_os = get_extension_os(filename)
        ext_pathlib = get_extension_pathlib(filename)
        print(f"{filename:<30} {ext_os or '(none)':>10} {ext_pathlib or '(none)':>10}")


if __name__ == "__main__":
    main()
