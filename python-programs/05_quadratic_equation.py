"""Program 5: Solve Quadratic Equation

Solves a quadratic equation of the form ax² + bx + c = 0 using the
quadratic formula, handling real and complex roots.

Reference: https://www.programiz.com/python-programming/examples/quadratic-roots
"""

import cmath


def solve_quadratic(a: float, b: float, c: float) -> tuple:
    """Solve the quadratic equation ax² + bx + c = 0.

    Args:
        a: Coefficient of x².
        b: Coefficient of x.
        c: Constant term.

    Returns:
        A tuple of two roots (may be complex).

    Raises:
        ValueError: If 'a' is zero (not a quadratic equation).
    """
    if a == 0:
        raise ValueError("Coefficient 'a' must be non-zero for a quadratic equation")

    discriminant = (b ** 2) - (4 * a * c)

    # Using cmath to handle both real and complex roots
    root1 = (-b + cmath.sqrt(discriminant)) / (2 * a)
    root2 = (-b - cmath.sqrt(discriminant)) / (2 * a)

    return root1, root2


def format_root(root: complex) -> str:
    """Format a root for display, showing real numbers without imaginary part."""
    if root.imag == 0:
        return f"{root.real:.2f}"
    return f"{root:.2f}"


def main() -> None:
    """Read coefficients and solve the quadratic equation."""
    print("Solve: ax² + bx + c = 0")
    a = float(input("Enter coefficient a: "))
    b = float(input("Enter coefficient b: "))
    c = float(input("Enter coefficient c: "))

    root1, root2 = solve_quadratic(a, b, c)

    print(f"\nThe solutions are:")
    print(f"  x₁ = {format_root(root1)}")
    print(f"  x₂ = {format_root(root2)}")


if __name__ == "__main__":
    main()
