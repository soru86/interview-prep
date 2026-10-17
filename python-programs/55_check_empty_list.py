"""Program 55: Check If a List is Empty

Demonstrates multiple ways to check if a list is empty in Python.

Reference: https://www.programiz.com/python-programming/examples/check-empty-list
"""


def main() -> None:
    """Demonstrate checking if a list is empty."""
    empty_list: list = []
    non_empty_list = [1, 2, 3]

    # Method 1: Pythonic truth value testing (recommended)
    print("Method 1: Truth value testing")
    if not empty_list:
        print(f"  {empty_list} is empty")
    if non_empty_list:
        print(f"  {non_empty_list} is not empty")

    # Method 2: Comparing with []
    print("\nMethod 2: Compare with []")
    if empty_list == []:
        print(f"  {empty_list} is empty")

    # Method 3: Using len()
    print("\nMethod 3: Using len()")
    if len(empty_list) == 0:
        print(f"  {empty_list} is empty (length = 0)")
    print(f"  {non_empty_list} has length = {len(non_empty_list)}")


if __name__ == "__main__":
    main()
