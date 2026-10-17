"""Program 17: Display the Multiplication Table

Displays the multiplication table for a given number.

Reference: https://www.programiz.com/python-programming/examples/multiplication-table
"""


def multiplication_table(num: int, up_to: int = 10) -> list[str]:
    """Generate the multiplication table for a number.

    Args:
        num: The number to create a table for.
        up_to: How many multiples to display (default 10).

    Returns:
        A list of formatted strings representing the table.
    """
    return [f"{num} x {i} = {num * i}" for i in range(1, up_to + 1)]


def main() -> None:
    """Read a number and display its multiplication table."""
    num = int(input("Enter a number: "))

    print(f"\nMultiplication Table for {num}:")
    print("-" * 20)
    for line in multiplication_table(num):
        print(line)


if __name__ == "__main__":
    main()
