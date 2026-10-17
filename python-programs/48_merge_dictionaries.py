"""Program 48: Merge Two Dictionaries

Demonstrates multiple ways to merge two dictionaries in Python.

Reference: https://www.programiz.com/python-programming/examples/merge-dictionaries
"""


def merge_with_update(dict1: dict, dict2: dict) -> dict:
    """Merge two dictionaries using the update() method."""
    merged = dict1.copy()
    merged.update(dict2)
    return merged


def merge_with_unpacking(dict1: dict, dict2: dict) -> dict:
    """Merge two dictionaries using ** unpacking (Python 3.5+)."""
    return {**dict1, **dict2}


def merge_with_pipe(dict1: dict, dict2: dict) -> dict:
    """Merge two dictionaries using the | operator (Python 3.9+)."""
    return dict1 | dict2


def main() -> None:
    """Demonstrate different ways to merge dictionaries."""
    dict1 = {"a": 1, "b": 2, "c": 3}
    dict2 = {"c": 30, "d": 4, "e": 5}

    print(f"Dict 1: {dict1}")
    print(f"Dict 2: {dict2}")
    print("-" * 40)

    # Method 1: Using update()
    result1 = merge_with_update(dict1, dict2)
    print(f"Merged (update):     {result1}")

    # Method 2: Using ** unpacking
    result2 = merge_with_unpacking(dict1, dict2)
    print(f"Merged (unpacking):  {result2}")

    # Method 3: Using | operator (Python 3.9+)
    result3 = merge_with_pipe(dict1, dict2)
    print(f"Merged (| operator): {result3}")


if __name__ == "__main__":
    main()
