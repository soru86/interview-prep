"""Program 37: Transpose a Matrix

Demonstrates transposing a matrix (swapping rows and columns)
using nested list comprehension and zip().

Reference: https://www.programiz.com/python-programming/examples/transpose-matrix
"""


def transpose_comprehension(matrix: list[list[float]]) -> list[list[float]]:
    """Transpose a matrix using nested list comprehension."""
    rows = len(matrix)
    cols = len(matrix[0])
    return [[matrix[i][j] for i in range(rows)] for j in range(cols)]


def transpose_zip(matrix: list[list[float]]) -> list[list[float]]:
    """Transpose a matrix using zip() — more Pythonic."""
    return [list(row) for row in zip(*matrix)]


def print_matrix(matrix: list[list[float]], label: str = "") -> None:
    """Print a matrix in a formatted way."""
    if label:
        print(f"{label}:")
    for row in matrix:
        print("  ", row)
    print()


def main() -> None:
    """Demonstrate matrix transposition with a sample matrix."""
    matrix = [
        [12, 7],
        [4, 5],
        [3, 8],
    ]

    print_matrix(matrix, "Original Matrix (3x2)")

    transposed = transpose_zip(matrix)
    print_matrix(transposed, "Transposed Matrix (2x3)")


if __name__ == "__main__":
    main()
