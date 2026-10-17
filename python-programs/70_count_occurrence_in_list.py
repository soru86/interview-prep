"""Program 70: Count the Occurrence of an Item in a List

Demonstrates counting how many times an item appears in a list.

Reference: https://www.programiz.com/python-programming/examples/occurrence-of-item
"""

from collections import Counter


def main() -> None:
    """Demonstrate counting occurrences in a list."""
    fruits = ["apple", "banana", "cherry", "apple", "banana", "apple", "date"]

    print(f"List: {fruits}\n")

    # Method 1: Using list.count()
    item = "apple"
    count = fruits.count(item)
    print(f"Method 1 — '{item}'.count(): {count}")

    # Method 2: Using collections.Counter
    counter = Counter(fruits)
    print(f"\nMethod 2 — Counter: {dict(counter)}")
    print(f"  Most common: {counter.most_common(2)}")

    # Method 3: Using a loop
    count_manual = sum(1 for fruit in fruits if fruit == item)
    print(f"\nMethod 3 — Manual count of '{item}': {count_manual}")


if __name__ == "__main__":
    main()
