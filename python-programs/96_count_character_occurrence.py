"""Program 96: Count the Number of Occurrence of a Character in String

Demonstrates counting character occurrences using built-in string methods
and collections.

Reference: https://www.programiz.com/python-programming/examples/character-occurrence
"""

from collections import Counter


def main() -> None:
    """Demonstrate counting character occurrences in a string."""
    text = "python programming is awesome"
    char_to_find = "m"
    
    print(f"String: '{text}'\n")
    
    # Method 1: Using str.count() (Recommended for single character)
    count1 = text.count(char_to_find)
    print(f"Method 1 — '{char_to_find}' appears {count1} times (using count())")
    
    # Method 2: Using a loop
    count2 = sum(1 for c in text if c == char_to_find)
    print(f"Method 2 — '{char_to_find}' appears {count2} times (using loop)")
    
    # Method 3: Counting ALL characters using collections.Counter
    counts = Counter(text)
    print(f"\nMethod 3 — Counting all characters:")
    
    # Show top 5 most common characters (excluding spaces)
    non_space_counts = Counter(text.replace(" ", ""))
    for char, count in non_space_counts.most_common(5):
        print(f"  '{char}': {count}")


if __name__ == "__main__":
    main()
