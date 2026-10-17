"""Program 8: Convert Kilometers to Miles

Demonstrates unit conversion from kilometers to miles.

Reference: https://www.programiz.com/python-programming/examples/km-mile
"""

KM_TO_MILES_FACTOR = 0.621371


def km_to_miles(kilometers: float) -> float:
    """Convert kilometers to miles."""
    return kilometers * KM_TO_MILES_FACTOR


def miles_to_km(miles: float) -> float:
    """Convert miles to kilometers."""
    return miles / KM_TO_MILES_FACTOR


def main() -> None:
    """Read kilometers and display the equivalent in miles."""
    km = float(input("Enter distance in kilometers: "))

    miles = km_to_miles(km)
    print(f"{km:.2f} kilometers = {miles:.2f} miles")


if __name__ == "__main__":
    main()
