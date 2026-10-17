"""Program 80: Get the File Name From the File Path

Demonstrates extracting the filename from a full file path.

Reference: https://www.programiz.com/python-programming/examples/file-name-from-file-path
"""

import os
from pathlib import Path


def main() -> None:
    """Demonstrate extracting filenames from paths."""
    paths = [
        "/home/user/documents/report.pdf",
        "/var/log/syslog",
        "C:\\Users\\admin\\file.txt",
        "relative/path/to/data.csv",
        "/path/to/archive.tar.gz",
    ]

    print(f"{'Full Path':<45} {'os.path':>20} {'pathlib':>20}")
    print("-" * 87)

    for path in paths:
        name_os = os.path.basename(path)
        name_pathlib = Path(path).name
        print(f"{path:<45} {name_os:>20} {name_pathlib:>20}")

    # Getting filename without extension
    print("\n--- Filename without extension ---")
    sample = "/home/user/photo.jpg"
    print(f"  os.path.splitext: {os.path.splitext(os.path.basename(sample))[0]}")
    print(f"  pathlib.stem:     {Path(sample).stem}")


if __name__ == "__main__":
    main()
