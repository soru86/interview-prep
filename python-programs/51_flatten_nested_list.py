"""Program 51: Flatten a Nested List

Demonstrates flattening a nested (irregular) list into a single flat list.

Reference: https://www.programiz.com/python-programming/examples/flatten-nested-list
"""

from collections.abc import Iterable


def flatten(nested_list: list) -> list:
    """Flatten a nested list of arbitrary depth.

    Args:
        nested_list: A list that may contain other lists.

    Returns:
        A flat list with all nested elements.
    """
    flat = []
    for item in nested_list:
        if isinstance(item, Iterable) and not isinstance(item, (str, bytes)):
            flat.extend(flatten(item))
        else:
            flat.append(item)
    return flat


def flatten_one_level(nested_list: list[list]) -> list:
    """Flatten a list one level deep using list comprehension."""
    return [item for sublist in nested_list for item in sublist]


def main() -> None:
    """Demonstrate list flattening."""
    # One level deep
    nested_1 = [[1, 2, 3], [4, 5], [6, 7, 8, 9]]
    print(f"Original:  {nested_1}")
    print(f"Flattened: {flatten_one_level(nested_1)}\n")

    # Arbitrary depth
    nested_2 = [1, [2, 3], [4, [5, [6, 7]]], 8]
    print(f"Original:  {nested_2}")
    print(f"Flattened: {flatten(nested_2)}")


if __name__ == "__main__":
    main()
