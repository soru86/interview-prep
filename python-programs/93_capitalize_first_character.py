"""Program 93: Capitalize the First Character of a String

Demonstrates how to capitalize the first character of a string
while preserving or modifying the rest.

Reference: https://www.programiz.com/python-programming/examples/capitalize-first-character
"""


def main() -> None:
    """Demonstrate string capitalization methods."""
    text = "python programming is fun"
    
    print(f"Original:        '{text}'\n")
    
    # Method 1: capitalize() - lowercases the rest of the string
    print(f"1. capitalize(): '{text.capitalize()}'")
    
    # Method 2: title() - capitalizes first letter of EVERY word
    print(f"2. title():      '{text.title()}'")
    
    # Method 3: string slicing (preserves rest of string's case)
    mixed_case = "pYtHoN"
    sliced = mixed_case[0].upper() + mixed_case[1:]
    print(f"\nOriginal mixed:  '{mixed_case}'")
    print(f"3. Slicing:      '{sliced}'")
    print(f"   capitalize(): '{mixed_case.capitalize()}' (notice the difference)")


if __name__ == "__main__":
    main()
