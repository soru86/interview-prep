"""Program 64: Get the Last Element of the List

Demonstrates multiple ways to access the last element of a list.

Reference: https://www.programiz.com/python-programming/examples/list-element-list
"""


def main() -> None:
    """Demonstrate getting the last element of a list."""
    fruits = ["apple", "banana", "cherry", "date", "elderberry"]

    print(f"List: {fruits}\n")

    # Method 1: Negative indexing (recommended)
    print(f"Method 1 - fruits[-1]:    {fruits[-1]}")

    # Method 2: Using len()
    print(f"Method 2 - fruits[len-1]: {fruits[len(fruits) - 1]}")

    # Method 3: Using pop() — modifies the list
    fruits_copy = fruits.copy()
    last = fruits_copy.pop()
    print(f"Method 3 - pop():         {last}")

    # Method 4: Using slicing
    print(f"Method 4 - fruits[-1:]:   {fruits[-1:]}")

    # Accessing last N elements
    n = 3
    print(f"\nLast {n} elements: {fruits[-n:]}")


if __name__ == "__main__":
    main()
