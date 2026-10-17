"""Program 81: Represent enum

Demonstrates creating and using enumerations with Python's enum module.

Reference: https://www.programiz.com/python-programming/examples/represent-enum
"""

from enum import Enum, auto


class Color(Enum):
    """An enumeration of colors."""
    RED = 1
    GREEN = 2
    BLUE = 3


class Direction(Enum):
    """An enumeration of directions using auto()."""
    NORTH = auto()
    SOUTH = auto()
    EAST = auto()
    WEST = auto()


class Status(Enum):
    """HTTP status codes as an enumeration."""
    OK = 200
    NOT_FOUND = 404
    SERVER_ERROR = 500


def main() -> None:
    """Demonstrate enum usage."""
    # Accessing enum members
    print("=== Color Enum ===")
    print(f"Color.RED:       {Color.RED}")
    print(f"Color.RED.name:  {Color.RED.name}")
    print(f"Color.RED.value: {Color.RED.value}")

    # Iterating over enum
    print("\n=== All Colors ===")
    for color in Color:
        print(f"  {color.name} = {color.value}")

    # Direction with auto()
    print("\n=== Direction Enum (auto) ===")
    for direction in Direction:
        print(f"  {direction.name} = {direction.value}")

    # Comparison
    print(f"\n=== Comparisons ===")
    print(f"Color.RED == Color.RED:   {Color.RED == Color.RED}")
    print(f"Color.RED == Color.BLUE:  {Color.RED == Color.BLUE}")
    print(f"Color.RED is Color.RED:   {Color.RED is Color.RED}")

    # Lookup by value
    print(f"\nColor(2): {Color(2)}")
    print(f"Status(404): {Status(404)}")


if __name__ == "__main__":
    main()
