"""Program 50: Access Index of a List Using for Loop

Demonstrates accessing list elements with their indices using
enumerate() and range(len()).

Reference: https://www.programiz.com/python-programming/examples/index-for-loop
"""


def main() -> None:
    """Demonstrate different ways to access list indices."""
    fruits = ["apple", "banana", "cherry", "date", "elderberry"]

    # Method 1: Using enumerate() — recommended
    print("Method 1: Using enumerate()")
    for index, fruit in enumerate(fruits):
        print(f"  Index {index}: {fruit}")

    print()

    # Method 2: Using range(len()) — older style
    print("Method 2: Using range(len())")
    for i in range(len(fruits)):
        print(f"  Index {i}: {fruits[i]}")

    print()

    # Method 3: enumerate with custom start index
    print("Method 3: enumerate with start=1")
    for index, fruit in enumerate(fruits, start=1):
        print(f"  Item {index}: {fruit}")


if __name__ == "__main__":
    main()
