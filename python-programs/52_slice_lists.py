"""Program 52: Slice Lists

Demonstrates various list slicing techniques in Python.

Reference: https://www.programiz.com/python-programming/examples/list-slicing
"""


def main() -> None:
    """Demonstrate list slicing with examples."""
    letters = ["a", "b", "c", "d", "e", "f", "g", "h"]

    print(f"Original list: {letters}")
    print("-" * 40)

    # Basic slicing: list[start:stop:step]
    print(f"letters[2:5]     = {letters[2:5]}")       # ['c', 'd', 'e']
    print(f"letters[:3]      = {letters[:3]}")         # ['a', 'b', 'c']
    print(f"letters[5:]      = {letters[5:]}")         # ['f', 'g', 'h']
    print(f"letters[:]       = {letters[:]}")          # Full copy
    print(f"letters[-3:]     = {letters[-3:]}")        # Last 3
    print(f"letters[:-3]     = {letters[:-3]}")        # All except last 3

    # Slicing with step
    print(f"letters[::2]     = {letters[::2]}")        # Every 2nd element
    print(f"letters[1::2]    = {letters[1::2]}")       # Every 2nd, starting at 1
    print(f"letters[::-1]    = {letters[::-1]}")        # Reversed
    print(f"letters[-1::-2]  = {letters[-1::-2]}")     # Reverse every 2nd

    # Slice assignment
    numbers = [0, 1, 2, 3, 4, 5]
    print(f"\nOriginal numbers: {numbers}")
    numbers[2:4] = [20, 30]
    print(f"After numbers[2:4] = [20, 30]: {numbers}")


if __name__ == "__main__":
    main()
