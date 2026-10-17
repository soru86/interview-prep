"""Program 78: Differentiate Between type() and isinstance()

Explains the difference between type() and isinstance() for type checking.

Reference: https://www.programiz.com/python-programming/examples/type-vs-instance
"""


class Animal:
    """Base class for animals."""
    pass


class Dog(Animal):
    """Dog is a subclass of Animal."""
    pass


class Cat(Animal):
    """Cat is a subclass of Animal."""
    pass


def main() -> None:
    """Demonstrate the difference between type() and isinstance()."""
    dog = Dog()
    cat = Cat()

    print("=== type() — checks EXACT type ===")
    print(f"type(dog) == Dog:    {type(dog) == Dog}")      # True
    print(f"type(dog) == Animal: {type(dog) == Animal}")    # False (exact match)
    print(f"type(42) == int:     {type(42) == int}")        # True

    print("\n=== isinstance() — checks type AND inheritance ===")
    print(f"isinstance(dog, Dog):    {isinstance(dog, Dog)}")      # True
    print(f"isinstance(dog, Animal): {isinstance(dog, Animal)}")    # True (inheritance)
    print(f"isinstance(42, int):     {isinstance(42, int)}")        # True

    print("\n=== isinstance() with tuple of types ===")
    print(f"isinstance(dog, (Dog, Cat)):    {isinstance(dog, (Dog, Cat))}")
    print(f"isinstance(42, (int, float)):   {isinstance(42, (int, float))}")

    print("\n=== Key difference ===")
    print(f"type(dog) is Dog:       {type(dog) is Dog}")        # True
    print(f"type(dog) is Animal:    {type(dog) is Animal}")      # False
    print(f"isinstance(dog, Animal): {isinstance(dog, Animal)}")  # True
    print("\n→ isinstance() respects inheritance; type() does not.")


if __name__ == "__main__":
    main()
