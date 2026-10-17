"""Program 72: Delete an Element From a Dictionary

Demonstrates different ways to remove elements from a dictionary.

Reference: https://www.programiz.com/python-programming/examples/delete-from-dictionary
"""


def main() -> None:
    """Demonstrate deleting elements from a dictionary."""
    # Method 1: Using del
    person = {"name": "Alice", "age": 25, "city": "NYC", "email": "alice@example.com"}
    print(f"Original: {person}")
    del person["email"]
    print(f"After del 'email': {person}\n")

    # Method 2: Using pop() — returns the removed value
    person2 = {"name": "Bob", "age": 30, "city": "LA", "phone": "555-1234"}
    print(f"Original: {person2}")
    removed_value = person2.pop("phone")
    print(f"After pop('phone'): {person2}")
    print(f"Removed value: {removed_value}\n")

    # Method 3: Using pop() with default — avoids KeyError
    person3 = {"name": "Charlie", "age": 35}
    result = person3.pop("address", "Key not found")
    print(f"pop('address', default): {result}\n")

    # Method 4: Using popitem() — removes last inserted item
    person4 = {"name": "Diana", "age": 28, "role": "Engineer"}
    print(f"Original: {person4}")
    last_item = person4.popitem()
    print(f"After popitem(): {person4}")
    print(f"Removed item: {last_item}\n")

    # Method 5: Using dict comprehension to filter
    scores = {"math": 90, "science": 85, "art": 70, "history": 60}
    filtered = {k: v for k, v in scores.items() if v >= 80}
    print(f"Scores >= 80: {filtered}")


if __name__ == "__main__":
    main()
