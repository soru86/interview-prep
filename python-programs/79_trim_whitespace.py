"""Program 79: Trim Whitespace From a String

Demonstrates removing leading, trailing, and all whitespace from strings.

Reference: https://www.programiz.com/python-programming/examples/trim-whitespace
"""


def main() -> None:
    """Demonstrate different ways to trim whitespace."""
    text = "   Hello,   World!   "

    print(f'Original:         "{text}"')
    print(f'strip():          "{text.strip()}"')      # Both sides
    print(f'lstrip():         "{text.lstrip()}"')     # Left only
    print(f'rstrip():         "{text.rstrip()}"')     # Right only

    # Remove all whitespace
    no_spaces = "".join(text.split())
    print(f'Remove all spaces: "{no_spaces}"')

    # Replace multiple spaces with single space
    normalized = " ".join(text.split())
    print(f'Normalize spaces:  "{normalized}"')

    # Strip specific characters
    csv_line = "***Hello***"
    print(f'\n"{csv_line}".strip("*") = "{csv_line.strip("*")}"')


if __name__ == "__main__":
    main()
