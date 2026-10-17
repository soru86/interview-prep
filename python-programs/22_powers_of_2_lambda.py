"""Program 22: Display Powers of 2 Using Anonymous Function

Demonstrates the use of lambda (anonymous) functions to compute powers of 2.

Reference: https://www.programiz.com/python-programming/examples/power-anonymous
"""


def display_powers_of_2(n: int) -> list[int]:
    """Return a list of powers of 2 from 2^0 to 2^n using lambda."""
    power_of_2 = lambda x: 2 ** x  # noqa: E731 – intentional for demonstration
    return [power_of_2(i) for i in range(n + 1)]


def main() -> None:
    """Read n and display powers of 2 up to 2^n."""
    n = int(input("Display powers of 2 up to 2^n. Enter n: "))

    if n < 0:
        print("Please enter a non-negative integer.")
        return

    powers = display_powers_of_2(n)

    print(f"\nPowers of 2 from 2^0 to 2^{n}:")
    for i, value in enumerate(powers):
        print(f"  2^{i} = {value}")


if __name__ == "__main__":
    main()
