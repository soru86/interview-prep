"""Program 77: Convert Two Lists Into a Dictionary

Demonstrates combining two parallel lists into a dictionary.

Reference: https://www.programiz.com/python-programming/examples/list-to-dictionary
"""


def lists_to_dict_zip(keys: list, values: list) -> dict:
    """Convert two lists into a dictionary using zip()."""
    return dict(zip(keys, values))


def lists_to_dict_comprehension(keys: list, values: list) -> dict:
    """Convert two lists into a dictionary using dict comprehension."""
    return {k: v for k, v in zip(keys, values)}


def main() -> None:
    """Demonstrate converting two lists into a dictionary."""
    keys = ["name", "age", "city", "country"]
    values = ["Alice", 30, "New York", "USA"]

    print(f"Keys:   {keys}")
    print(f"Values: {values}\n")

    # Method 1: Using dict(zip())
    result1 = lists_to_dict_zip(keys, values)
    print(f"dict(zip()):       {result1}")

    # Method 2: Using dict comprehension
    result2 = lists_to_dict_comprehension(keys, values)
    print(f"Dict comprehension: {result2}")

    # Handling unequal lengths — zip truncates to shortest
    keys2 = ["a", "b", "c", "d", "e"]
    values2 = [1, 2, 3]
    print(f"\nUnequal lengths: {dict(zip(keys2, values2))}")


if __name__ == "__main__":
    main()
