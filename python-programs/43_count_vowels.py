"""Program 43: Count the Number of Each Vowel

Counts the occurrences of each vowel (a, e, i, o, u) in a string.

Reference: https://www.programiz.com/python-programming/examples/count-vowel
"""


def count_vowels(text: str) -> dict[str, int]:
    """Count the occurrence of each vowel in the text.

    Args:
        text: The input string.

    Returns:
        A dictionary mapping each vowel to its count.
    """
    vowels = "aeiou"
    text_lower = text.lower()
    return {v: text_lower.count(v) for v in vowels}


def main() -> None:
    """Read a string and display the count of each vowel."""
    text = input("Enter a string: ")

    counts = count_vowels(text)

    print("\nVowel counts:")
    for vowel, count in counts.items():
        print(f"  '{vowel}': {count}")

    total = sum(counts.values())
    print(f"\nTotal vowels: {total}")


if __name__ == "__main__":
    main()
