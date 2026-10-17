"""Program 47: Create Pyramid Patterns

Demonstrates various pyramid and triangle patterns using nested loops.

Reference: https://www.programiz.com/python-programming/examples/pyramid-patterns
"""


def full_pyramid(rows: int) -> None:
    """Print a full pyramid of stars."""
    for i in range(1, rows + 1):
        print(" " * (rows - i) + "* " * i)


def inverted_pyramid(rows: int) -> None:
    """Print an inverted full pyramid of stars."""
    for i in range(rows, 0, -1):
        print(" " * (rows - i) + "* " * i)


def right_triangle(rows: int) -> None:
    """Print a right-angled triangle of stars."""
    for i in range(1, rows + 1):
        print("* " * i)


def number_pyramid(rows: int) -> None:
    """Print a pyramid of numbers."""
    for i in range(1, rows + 1):
        print(" " * (rows - i), end="")
        for j in range(1, i + 1):
            print(j, end=" ")
        print()


def floyd_triangle(rows: int) -> None:
    """Print Floyd's triangle."""
    number = 1
    for i in range(1, rows + 1):
        for _ in range(i):
            print(f"{number:<4}", end="")
            number += 1
        print()


def main() -> None:
    """Display various pyramid patterns."""
    rows = 5

    print("=" * 30)
    print("1. Full Pyramid")
    print("=" * 30)
    full_pyramid(rows)

    print(f"\n{'=' * 30}")
    print("2. Inverted Pyramid")
    print("=" * 30)
    inverted_pyramid(rows)

    print(f"\n{'=' * 30}")
    print("3. Right Triangle")
    print("=" * 30)
    right_triangle(rows)

    print(f"\n{'=' * 30}")
    print("4. Number Pyramid")
    print("=" * 30)
    number_pyramid(rows)

    print(f"\n{'=' * 30}")
    print("5. Floyd's Triangle")
    print("=" * 30)
    floyd_triangle(rows)


if __name__ == "__main__":
    main()
