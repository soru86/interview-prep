"""Program 87: Iterate Through Two Lists in Parallel

Demonstrates iterating through two (or more) lists simultaneously using zip().

Reference: https://www.programiz.com/python-programming/examples/iterate-two-lists-parallelly
"""

from itertools import zip_longest


def main() -> None:
    """Demonstrate parallel list iteration."""
    names = ["Alice", "Bob", "Charlie", "Diana"]
    scores = [95, 82, 78, 91]

    # Method 1: Using zip() — stops at shortest
    print("Method 1 — zip():")
    for name, score in zip(names, scores):
        print(f"  {name}: {score}")

    # Method 2: Using zip() with three lists
    print("\nMethod 2 — zip() with three lists:")
    grades = ["A", "B", "C", "A"]
    for name, score, grade in zip(names, scores, grades):
        print(f"  {name}: {score} (Grade {grade})")

    # Method 3: zip_longest — pads shorter lists with fillvalue
    print("\nMethod 3 — zip_longest():")
    colors = ["red", "blue"]
    sizes = ["S", "M", "L", "XL"]
    for color, size in zip_longest(colors, sizes, fillvalue="N/A"):
        print(f"  Color: {color}, Size: {size}")

    # Method 4: Using enumerate with zip
    print("\nMethod 4 — enumerate with zip:")
    for i, (name, score) in enumerate(zip(names, scores), 1):
        print(f"  {i}. {name} scored {score}")


if __name__ == "__main__":
    main()
