"""Program 92: Check If Two Strings are Anagram

Demonstrates checking if two strings are anagrams of each other.
An anagram is formed by rearranging the letters of a different word.

Reference: https://www.programiz.com/python-programming/examples/anagram
"""

from collections import Counter


def are_anagrams_sort(str1: str, str2: str) -> bool:
    """Check if strings are anagrams by sorting them."""
    # Normalize by converting to lowercase and removing spaces
    s1 = str1.replace(" ", "").lower()
    s2 = str2.replace(" ", "").lower()
    return sorted(s1) == sorted(s2)


def are_anagrams_counter(str1: str, str2: str) -> bool:
    """Check if strings are anagrams using collections.Counter."""
    s1 = str1.replace(" ", "").lower()
    s2 = str2.replace(" ", "").lower()
    return Counter(s1) == Counter(s2)


def main() -> None:
    """Demonstrate anagram checking."""
    pairs = [
        ("Listen", "Silent"),
        ("Triangle", "Integral"),
        ("Hello", "World"),
        ("Dormitory", "Dirty room"),
    ]
    
    print("Anagram Check:")
    print("-" * 50)
    for s1, s2 in pairs:
        is_anagram = are_anagrams_counter(s1, s2)
        status = "Yes" if is_anagram else "No"
        print(f"'{s1}' & '{s2}' -> Anagram? {status}")


if __name__ == "__main__":
    main()
