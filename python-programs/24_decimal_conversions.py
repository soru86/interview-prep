"""Program 24: Convert Decimal to Binary, Octal and Hexadecimal

Demonstrates converting a decimal integer to binary, octal, and hexadecimal
using Python's built-in functions.

Reference: https://www.programiz.com/python-programming/examples/conversion-binary-octal-hexadecimal
"""


def decimal_to_binary(n: int) -> str:
    """Convert decimal to binary string."""
    return bin(n)


def decimal_to_octal(n: int) -> str:
    """Convert decimal to octal string."""
    return oct(n)


def decimal_to_hexadecimal(n: int) -> str:
    """Convert decimal to hexadecimal string."""
    return hex(n)


def main() -> None:
    """Read a decimal number and display its binary, octal, and hex forms."""
    dec = int(input("Enter a decimal number: "))

    print(f"\nDecimal:     {dec}")
    print(f"Binary:      {decimal_to_binary(dec)}")
    print(f"Octal:       {decimal_to_octal(dec)}")
    print(f"Hexadecimal: {decimal_to_hexadecimal(dec)}")


if __name__ == "__main__":
    main()
