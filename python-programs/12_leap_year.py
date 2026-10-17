"""Program 12: Check Leap Year

Determines whether a given year is a leap year using the standard rules:
- Divisible by 4 AND not divisible by 100, OR
- Divisible by 400.

Reference: https://www.programiz.com/python-programming/examples/leap-year
"""

import calendar


def is_leap_year(year: int) -> bool:
    """Return True if the year is a leap year, False otherwise."""
    return (year % 4 == 0 and year % 100 != 0) or (year % 400 == 0)


def main() -> None:
    """Read a year and check if it is a leap year."""
    year = int(input("Enter a year: "))

    if is_leap_year(year):
        print(f"{year} is a leap year")
    else:
        print(f"{year} is not a leap year")

    # Verification using calendar module
    assert is_leap_year(year) == calendar.isleap(year)


if __name__ == "__main__":
    main()
