"""Program 41: Sort Words in Alphabetic Order

Sorts the words in a sentence alphabetically.

Reference: https://www.programiz.com/python-programming/examples/alphabetical-order
"""


def sort_words(sentence: str) -> list[str]:
    """Return the words in the sentence sorted alphabetically (case-insensitive)."""
    words = sentence.split()
    return sorted(words, key=str.lower)


def main() -> None:
    """Read a sentence and display its words sorted alphabetically."""
    sentence = input("Enter a sentence: ")

    sorted_words = sort_words(sentence)

    print(f"\nOriginal: {sentence}")
    print(f"Sorted:   {' '.join(sorted_words)}")


if __name__ == "__main__":
    main()
