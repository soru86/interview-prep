"""Program 65: Get a Substring of a String

Demonstrates extracting substrings using slicing.

Reference: https://www.programiz.com/python-programming/examples/substring-of-string
"""


def main() -> None:
    """Demonstrate substring extraction with slicing."""
    text = "Hello, World!"

    print(f'Original string: "{text}"\n')

    # Basic slicing: string[start:end]
    print(f'text[0:5]    = "{text[0:5]}"')       # "Hello"
    print(f'text[7:12]   = "{text[7:12]}"')       # "World"
    print(f'text[:5]     = "{text[:5]}"')          # "Hello"
    print(f'text[7:]     = "{text[7:]}"')          # "World!"

    # Negative indexing
    print(f'text[-6:]    = "{text[-6:]}"')          # "orld!"
    print(f'text[-6:-1]  = "{text[-6:-1]}"')        # "orld"

    # With step
    print(f'text[::2]    = "{text[::2]}"')          # Every 2nd char
    print(f'text[::-1]   = "{text[::-1]}"')          # Reversed

    # Check if substring exists
    substring = "World"
    print(f'\n"{substring}" in text: {"World" in text}')
    print(f'Index of "{substring}": {text.index(substring)}')


if __name__ == "__main__":
    main()
