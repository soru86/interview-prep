"""Program 54: Sort a Dictionary by Value

Demonstrates sorting a dictionary by its values in ascending and descending order.

Reference: https://www.programiz.com/python-programming/examples/sort-dictionary-value
"""


def sort_dict_by_value(d: dict, reverse: bool = False) -> dict:
    """Sort a dictionary by its values.

    Args:
        d: The dictionary to sort.
        reverse: If True, sort in descending order.

    Returns:
        A new dictionary sorted by values.
    """
    return dict(sorted(d.items(), key=lambda item: item[1], reverse=reverse))


def main() -> None:
    """Demonstrate sorting a dictionary by value."""
    scores = {"Alice": 85, "Bob": 92, "Charlie": 78, "Diana": 95, "Eve": 88}

    print(f"Original:   {scores}")

    # Sort ascending
    ascending = sort_dict_by_value(scores)
    print(f"Ascending:  {ascending}")

    # Sort descending
    descending = sort_dict_by_value(scores, reverse=True)
    print(f"Descending: {descending}")


if __name__ == "__main__":
    main()
