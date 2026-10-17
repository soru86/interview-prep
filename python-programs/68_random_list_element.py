"""Program 68: Randomly Select an Element From the List

Demonstrates randomly selecting elements from a list using the random module.

Reference: https://www.programiz.com/python-programming/examples/random-list-element
"""

import random
import secrets


def main() -> None:
    """Demonstrate random selection from a list."""
    colors = ["red", "blue", "green", "yellow", "purple", "orange", "pink"]

    print(f"List: {colors}\n")

    # Method 1: random.choice() — single element
    selected = random.choice(colors)
    print(f"random.choice():     {selected}")

    # Method 2: random.choices() — multiple (with replacement)
    selected_multiple = random.choices(colors, k=3)
    print(f"random.choices(k=3): {selected_multiple}")

    # Method 3: random.sample() — multiple (without replacement)
    selected_sample = random.sample(colors, k=3)
    print(f"random.sample(k=3):  {selected_sample}")

    # Method 4: secrets.choice() — cryptographically secure
    secure_pick = secrets.choice(colors)
    print(f"secrets.choice():    {secure_pick}")

    # Method 5: random.randrange with index
    random_index = random.randrange(len(colors))
    print(f"Random index [{random_index}]:    {colors[random_index]}")


if __name__ == "__main__":
    main()
