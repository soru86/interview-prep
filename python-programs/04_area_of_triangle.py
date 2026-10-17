"""Program 4: Calculate the Area of a Triangle

Demonstrates calculating the area of a triangle given its three sides
using Heron's formula.

Reference: https://www.programiz.com/python-programming/examples/area-triangle
"""

import math


def area_of_triangle(a: float, b: float, c: float) -> float:
    """Calculate the area of a triangle using Heron's formula.

    Args:
        a: Length of side a.
        b: Length of side b.
        c: Length of side c.

    Returns:
        The area of the triangle.

    Raises:
        ValueError: If the sides cannot form a valid triangle.
    """
    if a + b <= c or a + c <= b or b + c <= a:
        raise ValueError("The given sides do not form a valid triangle")

    # Semi-perimeter
    s = (a + b + c) / 2

    # Heron's formula
    area = math.sqrt(s * (s - a) * (s - b) * (s - c))
    return area


def main() -> None:
    """Read three sides and display the area of the triangle."""
    a = float(input("Enter side a: "))
    b = float(input("Enter side b: "))
    c = float(input("Enter side c: "))

    result = area_of_triangle(a, b, c)
    print(f"The area of the triangle is {result:.2f}")


if __name__ == "__main__":
    main()
