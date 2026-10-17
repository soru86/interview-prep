"""Program 36: Add Two Matrices

Demonstrates adding two matrices using nested list comprehension.

Reference: https://www.programiz.com/python-programming/examples/add-matrix
"""


def add_matrices(matrix_a: list[list[float]], matrix_b: list[list[float]]) -> list[list[float]]:
    """Add two matrices element-wise.

    Args:
        matrix_a: First matrix.
        matrix_b: Second matrix (same dimensions as matrix_a).

    Returns:
        The resulting matrix after addition.
    """
    return [
        [matrix_a[i][j] + matrix_b[i][j] for j in range(len(matrix_a[0]))]
        for i in range(len(matrix_a))
    ]


def print_matrix(matrix: list[list[float]], label: str = "") -> None:
    """Print a matrix in a formatted way."""
    if label:
        print(f"{label}:")
    for row in matrix:
        print("  ", row)
    print()


def main() -> None:
    """Demonstrate matrix addition with sample matrices."""
    matrix_a = [
        [12, 7, 3],
        [4, 5, 6],
        [7, 8, 9],
    ]

    matrix_b = [
        [5, 8, 1],
        [6, 7, 3],
        [4, 5, 9],
    ]

    print_matrix(matrix_a, "Matrix A")
    print_matrix(matrix_b, "Matrix B")

    result = add_matrices(matrix_a, matrix_b)
    print_matrix(result, "A + B")


if __name__ == "__main__":
    main()
