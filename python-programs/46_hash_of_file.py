"""Program 46: Find Hash of File

Computes the hash (MD5, SHA-1, SHA-256) of a file.
Reads in chunks for memory efficiency on large files.

Reference: https://www.programiz.com/python-programming/examples/hash-file
"""

import hashlib
import os

BUFFER_SIZE = 65536  # 64 KB


def compute_file_hash(filepath: str, algorithm: str = "sha256") -> str:
    """Compute the hash of a file using the specified algorithm.

    Args:
        filepath: Path to the file.
        algorithm: Hash algorithm name (e.g., 'md5', 'sha1', 'sha256').

    Returns:
        The hexadecimal hash string.
    """
    hasher = hashlib.new(algorithm)

    with open(filepath, "rb") as f:
        while True:
            data = f.read(BUFFER_SIZE)
            if not data:
                break
            hasher.update(data)

    return hasher.hexdigest()


def main() -> None:
    """Read a file path and display its hashes."""
    filepath = input("Enter the file path: ")

    if not os.path.isfile(filepath):
        print(f"File not found: {filepath}")
        return

    print(f"\nFile: {os.path.basename(filepath)}")
    print(f"Size: {os.path.getsize(filepath)} bytes\n")

    for algo in ("md5", "sha1", "sha256"):
        digest = compute_file_hash(filepath, algo)
        print(f"  {algo.upper():8s}: {digest}")


if __name__ == "__main__":
    main()
