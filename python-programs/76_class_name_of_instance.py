"""Program 76: Get the Class Name of an Instance

Demonstrates getting the class name of an object using type() and __class__.

Reference: https://www.programiz.com/python-programming/examples/class-name
"""


class Vehicle:
    """A simple Vehicle class for demonstration."""

    def __init__(self, name: str) -> None:
        self.name = name


class Car(Vehicle):
    """A Car subclass of Vehicle."""
    pass


def get_class_name(obj: object) -> str:
    """Return the class name of an object."""
    return type(obj).__name__


def main() -> None:
    """Demonstrate getting class names of instances."""
    # Built-in types
    values = [42, 3.14, "hello", [1, 2], {"a": 1}, (1, 2), {1, 2}, True]

    print("Built-in types:")
    for val in values:
        print(f"  {str(val):15s} -> {get_class_name(val)}")

    # Custom classes
    print("\nCustom classes:")
    vehicle = Vehicle("Bike")
    car = Car("Tesla")

    print(f"  vehicle -> {type(vehicle).__name__}")
    print(f"  car     -> {type(car).__name__}")

    # Using __class__.__name__
    print(f"\n  car.__class__.__name__ = {car.__class__.__name__}")

    # Checking class hierarchy
    print(f"\n  isinstance(car, Vehicle): {isinstance(car, Vehicle)}")
    print(f"  isinstance(car, Car):     {isinstance(car, Car)}")


if __name__ == "__main__":
    main()
