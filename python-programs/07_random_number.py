"""Program 7: Generate a Random Number

Demonstrates generating random numbers using Python's random module.

Reference: https://www.programiz.com/python-programming/examples/random-number
"""

import random


def generate_random_int(low: int, high: int) -> int:
    """Generate a random integer between low and high (inclusive)."""
    return random.randint(low, high)


def generate_random_float(low: float, high: float) -> float:
    """Generate a random float between low and high."""
    return random.uniform(low, high)


def main() -> None:
    """Generate and display random numbers."""
    # Random integer between 1 and 100
    rand_int = generate_random_int(1, 100)
    print(f"Random integer between 1 and 100: {rand_int}")

    # Random float between 0 and 1
    rand_float = random.random()
    print(f"Random float between 0 and 1:     {rand_float:.4f}")

    # Random float between 10 and 50
    rand_range = generate_random_float(10, 50)
    print(f"Random float between 10 and 50:   {rand_range:.4f}")


if __name__ == "__main__":
    main()
