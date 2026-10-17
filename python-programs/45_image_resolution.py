"""Program 45: Find the Size (Resolution) of an Image

Demonstrates reading image dimensions without external dependencies
by parsing the file header for common formats (PNG, JPEG, GIF, BMP).

Reference: https://www.programiz.com/python-programming/examples/resolution-image
"""

import struct
import os


def get_image_size(filepath: str) -> tuple[int, int] | None:
    """Get image dimensions by reading the file header.

    Supports PNG, JPEG, GIF, and BMP formats.

    Args:
        filepath: Path to the image file.

    Returns:
        A tuple (width, height) or None if format is unrecognized.
    """
    with open(filepath, "rb") as f:
        header = f.read(30)

        # PNG
        if header[:8] == b"\x89PNG\r\n\x1a\n":
            width, height = struct.unpack(">II", header[16:24])
            return width, height

        # GIF
        if header[:6] in (b"GIF87a", b"GIF89a"):
            width, height = struct.unpack("<HH", header[6:10])
            return width, height

        # BMP
        if header[:2] == b"BM":
            width, height = struct.unpack("<II", header[18:26])
            return width, abs(height)

        # JPEG — need to search for SOF markers
        if header[:2] == b"\xff\xd8":
            f.seek(2)
            while True:
                marker = f.read(2)
                if len(marker) < 2:
                    break
                if marker[0] != 0xFF:
                    break
                if marker[1] in (0xC0, 0xC1, 0xC2):
                    f.read(3)  # length + precision
                    height, width = struct.unpack(">HH", f.read(4))
                    return width, height
                else:
                    length = struct.unpack(">H", f.read(2))[0]
                    f.seek(length - 2, 1)

    return None


def main() -> None:
    """Demonstrate reading image dimensions."""
    filepath = input("Enter the image file path: ")

    if not os.path.isfile(filepath):
        print(f"File not found: {filepath}")
        return

    size = get_image_size(filepath)

    if size:
        width, height = size
        print(f"Image: {os.path.basename(filepath)}")
        print(f"Resolution: {width} x {height} pixels")
    else:
        print("Could not determine image size. Unsupported format.")


if __name__ == "__main__":
    main()
