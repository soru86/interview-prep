"""Program 97: Remove Duplicate Element From a List

Demonstrates removing duplicate elements from a list while either
preserving or ignoring the original order.

Reference: https://www.programiz.com/python-programming/examples/remove-duplicate-list
"""


def remove_duplicates_set(lst: list) -> list:
    """Remove duplicates by converting to a set (does NOT preserve order)."""
    return list(set(lst))


def remove_duplicates_ordered(lst: list) -> list:
    """Remove duplicates while preserving original order using dict."""
    # In Python 3.7+, standard dict maintains insertion order
    return list(dict.fromkeys(lst))


def remove_duplicates_loop(lst: list) -> list:
    """Remove duplicates while preserving order using a loop."""
    seen = set()
    result = []
    for item in lst:
        if item not in seen:
            seen.add(item)
            result.append(item)
    return result


def main() -> None:
    """Demonstrate removing duplicates from a list."""
    # Original list has duplicates
    numbers = [4, 2, 8, 4, 2, 9, 1, 8, 3, 2]
    
    print(f"Original list: {numbers}\n")
    
    # Method 1: set() (Order not guaranteed)
    unique_set = remove_duplicates_set(numbers)
    print(f"Method 1 (set)        : {unique_set}")
    
    # Method 2: dict.fromkeys() (Preserves order)
    unique_dict = remove_duplicates_ordered(numbers)
    print(f"Method 2 (fromkeys)   : {unique_dict}")
    
    # Method 3: Loop + Set (Preserves order)
    unique_loop = remove_duplicates_loop(numbers)
    print(f"Method 3 (loop + set) : {unique_loop}")


if __name__ == "__main__":
    main()
