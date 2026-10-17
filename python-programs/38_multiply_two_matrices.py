"""Program 38: Multiply Two Matrices

Demonstrates matrix multiplication using nested loops and list comprehension.

Reference: https://www.programiz.com/python-programming/examples/multiply-matrix
"""


def multiply_matrices(
    matrix_a: list[list[float]], matrix_b: list[list[float]]
) -> list[list[float]]:
    """Multiply two matrices (A × B).

    Args:
        matrix_a: First matrix (m × n).
        matrix_b: Second matrix (n × p).

    Returns:
        Resulting matrix (m × p).

    Raises:
        ValueError: If the matrices cannot be multiplied.
    """
    rows_a, cols_a = len(matrix_a), len(matrix_a[0])
    rows_b, cols_b = len(matrix_b), len(matrix_b[0])

    if cols_a != rows_b:
        raise ValueError(
            f"Cannot multiply: A has {cols_a} columns but B has {rows_b} rows"
        )

    result = [[0.0] * cols_b for _ in range(rows_a)]

    for i in range(rows_a):
        for j in range(cols_b):
            for k in range(cols_a):
                result[i][j] += matrix_a[i][k] * matrix_b[k][j]

    return result


def print_matrix(matrix: list[list[float]], label: str = "") -> None:
    """Print a matrix in a formatted way."""
    if label:
        print(f"{label}:")
    for row in matrix:
        print("  ", [round(x, 2) for x in row])
    print()


def main() -> None:
    """Demonstrate matrix multiplication with sample matrices."""
    matrix_a = [
        [12, 7, 3],
        [4, 5, 6],
        [7, 8, 9],
    ]

    matrix_b = [
        [5, 8],
        [6, 7],
        [4, 5],
    ]

    print_matrix(matrix_a, "Matrix A (3x3)")
    print_matrix(matrix_b, "Matrix B (3x2)")

    result = multiply_matrices(matrix_a, matrix_b)
    print_matrix(result, "A × B (3x2)")


if __name__ == "__main__":
    main()
