"""Program 94: Compute all the Permutation of the String

Demonstrates finding all permutations of a string using itertools
and recursion.

Reference: https://www.programiz.com/python-programming/examples/permutation-string
"""

import itertools


def get_permutations_itertools(s: str) -> list[str]:
    """Get all permutations using itertools.permutations."""
    # itertools.permutations returns tuples of characters
    # We join them to form strings
    return ["".join(p) for p in itertools.permutations(s)]


def get_permutations_recursive(s: str) -> list[str]:
    """Get all permutations using recursion."""
    if len(s) <= 1:
        return [s]
    
    perms = []
    for i, char in enumerate(s):
        # Extract the current character
        # Get permutations of the remaining characters
        remaining = s[:i] + s[i+1:]
        for p in get_permutations_recursive(remaining):
            perms.append(char + p)
            
    return perms


def main() -> None:
    """Demonstrate generating string permutations."""
    test_str = "ABC"
    
    print(f"String: '{test_str}'")
    print(f"Total expected permutations: 3! = 6\n")
    
    # Method 1: itertools
    perms1 = get_permutations_itertools(test_str)
    print("Method 1 (itertools):")
    print(f"  {perms1}")
    
    # Method 2: recursive
    perms2 = get_permutations_recursive(test_str)
    print("\nMethod 2 (recursive):")
    print(f"  {perms2}")
    
    # Using a string with duplicate characters
    dup_str = "AAB"
    unique_perms = set(get_permutations_itertools(dup_str))
    print(f"\nUnique permutations of '{dup_str}':")
    print(f"  {list(unique_perms)}")


if __name__ == "__main__":
    main()
