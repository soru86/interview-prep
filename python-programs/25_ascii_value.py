"""Program 25: Find ASCII Value of Character

Demonstrates finding the ASCII (Unicode code point) value of a character
using the ord() built-in function.

Reference: https://www.programiz.com/python-programming/examples/ascii-character
"""


def ascii_value(char: str) -> int:
    """Return the ASCII/Unicode code point of a character."""
    if len(char) != 1:
        raise ValueError("Input must be a single character")
    return ord(char)


def main() -> None:
    """Read a character and display its ASCII value."""
    char = input("Enter a character: ")

    if len(char) != 1:
        print("Please enter exactly one character.")
        return

    value = ascii_value(char)
    print(f"The ASCII value of '{char}' is {value}")

    # Reverse: convert ASCII value back to character
    print(f"chr({value}) = '{chr(value)}'")


if __name__ == "__main__":
    main()
