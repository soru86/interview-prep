"""Program 58: Concatenate Two Lists

Demonstrates multiple ways to concatenate (join) two lists in Python.

Reference: https://www.programiz.com/python-programming/examples/concatenate-two-lists
"""


def main() -> None:
    """Demonstrate different ways to concatenate lists."""
    list1 = [1, 2, 3]
    list2 = [4, 5, 6]

    print(f"List 1: {list1}")
    print(f"List 2: {list2}")
    print("-" * 30)

    # Method 1: Using + operator
    result1 = list1 + list2
    print(f"Using +       : {result1}")

    # Method 2: Using extend()
    result2 = list1.copy()
    result2.extend(list2)
    print(f"Using extend(): {result2}")

    # Method 3: Using * unpacking
    result3 = [*list1, *list2]
    print(f"Using * unpack: {result3}")

    # Method 4: Using list comprehension
    result4 = [item for lst in (list1, list2) for item in lst]
    print(f"Using listcomp: {result4}")


if __name__ == "__main__":
    main()
