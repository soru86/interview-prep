"""Program 18: Print the Fibonacci Sequence

Generates Fibonacci numbers up to a specified number of terms.
The sequence starts: 0, 1, 1, 2, 3, 5, 8, 13, 21, ...

Reference: https://www.programiz.com/python-programming/examples/fibonacci-sequence
"""


def fibonacci_sequence(n: int) -> list[int]:
    """Generate the first n Fibonacci numbers.

    Args:
        n: The number of terms to generate.

    Returns:
        A list of the first n Fibonacci numbers.
    """
    if n <= 0:
        return []
    if n == 1:
        return [0]

    sequence = [0, 1]
    for _ in range(2, n):
        sequence.append(sequence[-1] + sequence[-2])
    return sequence


def main() -> None:
    """Read the number of terms and display the Fibonacci sequence."""
    n_terms = int(input("How many Fibonacci terms to display? "))

    if n_terms <= 0:
        print("Please enter a positive integer.")
    else:
        sequence = fibonacci_sequence(n_terms)
        print(f"\nFibonacci sequence ({n_terms} terms):")
        print(", ".join(map(str, sequence)))


if __name__ == "__main__":
    main()
