"""Program 9: Convert Celsius to Fahrenheit

Demonstrates temperature conversion between Celsius and Fahrenheit.

Reference: https://www.programiz.com/python-programming/examples/celsius-fahrenheit
"""


def celsius_to_fahrenheit(celsius: float) -> float:
    """Convert Celsius to Fahrenheit."""
    return (celsius * 9 / 5) + 32


def fahrenheit_to_celsius(fahrenheit: float) -> float:
    """Convert Fahrenheit to Celsius."""
    return (fahrenheit - 32) * 5 / 9


def main() -> None:
    """Read temperature in Celsius and display in Fahrenheit."""
    celsius = float(input("Enter temperature in Celsius: "))

    fahrenheit = celsius_to_fahrenheit(celsius)
    print(f"{celsius:.2f}°C = {fahrenheit:.2f}°F")


if __name__ == "__main__":
    main()
