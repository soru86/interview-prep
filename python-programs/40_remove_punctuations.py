"""Program 40: Remove Punctuations From a String

Demonstrates removing all punctuation characters from a string.

Reference: https://www.programiz.com/python-programming/examples/remove-punctuation
"""

import string


def remove_punctuations(text: str) -> str:
    """Return the string with all punctuation characters removed."""
    return text.translate(str.maketrans("", "", string.punctuation))


def main() -> None:
    """Read a string and display it without punctuations."""
    text = input("Enter a string: ")

    cleaned = remove_punctuations(text)

    print(f"\nOriginal: {text}")
    print(f"Without punctuations: {cleaned}")


if __name__ == "__main__":
    main()
