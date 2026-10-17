"""Program 35: Convert Decimal to Binary Using Recursion

Converts a decimal number to its binary representation using recursion.

Reference: https://www.programiz.com/python-programming/examples/decimal-binary-recursion
"""


def decimal_to_binary_recursive(n: int) -> str:
    """Convert a non-negative decimal integer to binary string using recursion.

    Args:
        n: A non-negative integer.

    Returns:
        The binary representation as a string.
    """
    if n == 0:
        return "0"
    if n == 1:
        return "1"
    return decimal_to_binary_recursive(n // 2) + str(n % 2)


def main() -> None:
    """Read a decimal number and display its binary form."""
    dec = int(input("Enter a decimal number: "))

    if dec < 0:
        print("Please enter a non-negative integer.")
        return

    binary = decimal_to_binary_recursive(dec)
    print(f"Decimal {dec} = Binary {binary}")

    # Verification with built-in bin()
    print(f"Verification: {bin(dec)}")


if __name__ == "__main__":
    main()
