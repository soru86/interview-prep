"""Program 59: Check if a Key is Already Present in a Dictionary

Demonstrates different ways to check for key existence in a dictionary.

Reference: https://www.programiz.com/python-programming/examples/key-in-dictionary
"""


def main() -> None:
    """Demonstrate checking for key existence in a dictionary."""
    student = {
        "name": "Alice",
        "age": 21,
        "grade": "A",
    }

    print(f"Dictionary: {student}\n")

    # Method 1: Using 'in' keyword (recommended)
    key = "name"
    if key in student:
        print(f"'{key}' is present. Value: {student[key]}")
    else:
        print(f"'{key}' is not present")

    key = "email"
    if key in student:
        print(f"'{key}' is present. Value: {student[key]}")
    else:
        print(f"'{key}' is not present")

    # Method 2: Using .get() with default
    print(f"\n.get('name', 'N/A'):  {student.get('name', 'N/A')}")
    print(f".get('email', 'N/A'): {student.get('email', 'N/A')}")

    # Method 3: Using .keys()
    print(f"\n'grade' in student.keys(): {'grade' in student.keys()}")


if __name__ == "__main__":
    main()
