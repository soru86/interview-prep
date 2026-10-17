"""Program 39: Check Whether a String is Palindrome or Not

A palindrome reads the same forwards and backwards (e.g., 'radar', 'madam').

Reference: https://www.programiz.com/python-programming/examples/palindrome
"""


def is_palindrome(text: str) -> bool:
    """Return True if the string is a palindrome (case-insensitive).

    Ignores spaces and compares only alphanumeric characters.
    """
    cleaned = "".join(ch.lower() for ch in text if ch.isalnum())
    return cleaned == cleaned[::-1]


def main() -> None:
    """Read a string and check if it is a palindrome."""
    text = input("Enter a string: ")

    if is_palindrome(text):
        print(f'"{text}" is a palindrome')
    else:
        print(f'"{text}" is not a palindrome')


if __name__ == "__main__":
    main()
