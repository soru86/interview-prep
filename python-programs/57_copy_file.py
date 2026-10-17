"""Program 57: Copy a File

Demonstrates copying a file using shutil and manual read/write.

Reference: https://www.programiz.com/python-programming/examples/copy-file
"""

import shutil
import os
import tempfile


def copy_file_shutil(src: str, dst: str) -> None:
    """Copy a file using shutil.copy2 (preserves metadata)."""
    shutil.copy2(src, dst)


def copy_file_manual(src: str, dst: str) -> None:
    """Copy a file by reading and writing chunks manually."""
    buffer_size = 65536  # 64 KB
    with open(src, "rb") as f_src, open(dst, "wb") as f_dst:
        while True:
            chunk = f_src.read(buffer_size)
            if not chunk:
                break
            f_dst.write(chunk)


def main() -> None:
    """Demonstrate file copying."""
    # Create a temporary source file for demonstration
    with tempfile.NamedTemporaryFile(mode="w", suffix=".txt", delete=False) as tmp:
        tmp.write("Hello, this is a test file for copying.\n")
        tmp.write("It contains multiple lines of text.\n")
        src_path = tmp.name

    dst_path_1 = src_path + ".copy1"
    dst_path_2 = src_path + ".copy2"

    try:
        # Method 1: shutil.copy2
        copy_file_shutil(src_path, dst_path_1)
        print(f"Method 1 (shutil): Copied '{os.path.basename(src_path)}' -> '{os.path.basename(dst_path_1)}'")

        # Method 2: Manual copy
        copy_file_manual(src_path, dst_path_2)
        print(f"Method 2 (manual): Copied '{os.path.basename(src_path)}' -> '{os.path.basename(dst_path_2)}'")

        # Verify
        with open(src_path) as f:
            original = f.read()
        with open(dst_path_1) as f:
            copy1 = f.read()
        with open(dst_path_2) as f:
            copy2 = f.read()

        print(f"\nContents match (shutil): {original == copy1}")
        print(f"Contents match (manual): {original == copy2}")
    finally:
        # Clean up
        for path in (src_path, dst_path_1, dst_path_2):
            if os.path.exists(path):
                os.remove(path)


if __name__ == "__main__":
    main()
