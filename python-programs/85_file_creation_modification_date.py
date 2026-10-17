"""Program 85: Get File Creation and Modification Date

Demonstrates getting file timestamps (creation, modification, access).

Reference: https://www.programiz.com/python-programming/examples/file-modification-date
"""

import os
import time
from pathlib import Path
from datetime import datetime


def get_file_dates(filepath: str) -> dict[str, str]:
    """Get creation and modification dates of a file.

    Returns:
        A dictionary with 'modified', 'accessed', and 'created' timestamps.
    """
    stat = os.stat(filepath)

    return {
        "modified": datetime.fromtimestamp(stat.st_mtime).strftime("%Y-%m-%d %H:%M:%S"),
        "accessed": datetime.fromtimestamp(stat.st_atime).strftime("%Y-%m-%d %H:%M:%S"),
        "created": datetime.fromtimestamp(stat.st_ctime).strftime("%Y-%m-%d %H:%M:%S"),
    }


def main() -> None:
    """Display file creation and modification dates."""
    # Use this script file itself
    filepath = __file__

    print(f"File: {os.path.basename(filepath)}\n")

    dates = get_file_dates(filepath)
    for label, timestamp in dates.items():
        print(f"  {label.capitalize():10s}: {timestamp}")

    # Using pathlib
    path = Path(filepath)
    mod_time = datetime.fromtimestamp(path.stat().st_mtime)
    print(f"\n  pathlib modification: {mod_time}")

    # Using time.ctime for human-readable output
    print(f"  time.ctime(mtime):   {time.ctime(os.path.getmtime(filepath))}")


if __name__ == "__main__":
    main()
