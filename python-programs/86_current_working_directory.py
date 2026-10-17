"""Program 86: Get the Full Path of the Current Working Directory

Demonstrates getting the current working directory using os and pathlib.

Reference: https://www.programiz.com/python-programming/examples/current-working-directory
"""

import os
from pathlib import Path


def main() -> None:
    """Display the current working directory."""
    # Method 1: Using os.getcwd()
    cwd_os = os.getcwd()
    print(f"os.getcwd():     {cwd_os}")

    # Method 2: Using pathlib.Path.cwd()
    cwd_pathlib = Path.cwd()
    print(f"Path.cwd():      {cwd_pathlib}")

    # Method 3: Using os.path.abspath
    cwd_abspath = os.path.abspath(".")
    print(f"os.path.abspath: {cwd_abspath}")

    # Get the script's directory (not necessarily the CWD)
    script_dir = os.path.dirname(os.path.abspath(__file__))
    print(f"\nScript location: {script_dir}")

    # Verify all methods return the same result
    assert str(cwd_pathlib) == cwd_os == cwd_abspath


if __name__ == "__main__":
    main()
