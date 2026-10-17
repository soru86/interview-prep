"""Program 53: Iterate Over Dictionaries Using for Loop

Demonstrates multiple ways to iterate over dictionary keys, values, and items.

Reference: https://www.programiz.com/python-programming/examples/iterate-for-dictionary
"""


def main() -> None:
    """Demonstrate different ways to iterate over a dictionary."""
    student = {
        "name": "Alice",
        "age": 21,
        "major": "Computer Science",
        "gpa": 3.8,
    }

    # Method 1: Iterate over keys (default)
    print("1. Iterating over keys:")
    for key in student:
        print(f"   {key}")

    # Method 2: Iterate over values
    print("\n2. Iterating over values:")
    for value in student.values():
        print(f"   {value}")

    # Method 3: Iterate over key-value pairs
    print("\n3. Iterating over items (key-value pairs):")
    for key, value in student.items():
        print(f"   {key}: {value}")

    # Method 4: Iterate with enumerate for index
    print("\n4. With enumeration:")
    for index, (key, value) in enumerate(student.items(), 1):
        print(f"   {index}. {key} = {value}")


if __name__ == "__main__":
    main()
