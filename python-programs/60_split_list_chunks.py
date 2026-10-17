"""Program 60: Split a List Into Evenly Sized Chunks

Demonstrates splitting a list into smaller sublists of a specified size.

Reference: https://www.programiz.com/python-programming/examples/list-chunks
"""


def split_into_chunks(lst: list, chunk_size: int) -> list[list]:
    """Split a list into chunks of the specified size.

    Args:
        lst: The list to split.
        chunk_size: The maximum size of each chunk.

    Returns:
        A list of sublists (chunks).
    """
    return [lst[i:i + chunk_size] for i in range(0, len(lst), chunk_size)]


def split_into_chunks_generator(lst: list, chunk_size: int):
    """Yield successive chunks from a list (generator version)."""
    for i in range(0, len(lst), chunk_size):
        yield lst[i:i + chunk_size]


def main() -> None:
    """Demonstrate splitting a list into chunks."""
    data = list(range(1, 21))  # [1, 2, ..., 20]
    chunk_size = 5

    print(f"Original list: {data}")
    print(f"Chunk size: {chunk_size}\n")

    # Method 1: List comprehension
    chunks = split_into_chunks(data, chunk_size)
    print("Chunks (list comprehension):")
    for i, chunk in enumerate(chunks, 1):
        print(f"  Chunk {i}: {chunk}")

    # Method 2: Generator
    print("\nChunks (generator):")
    for i, chunk in enumerate(split_into_chunks_generator(data, chunk_size), 1):
        print(f"  Chunk {i}: {chunk}")


if __name__ == "__main__":
    main()
