"""Program 31: Display Calendar

Displays the calendar for a given month and year using the calendar module.

Reference: https://www.programiz.com/python-programming/examples/display-calendar
"""

import calendar


def display_month_calendar(year: int, month: int) -> str:
    """Return a formatted calendar string for the given month and year."""
    return calendar.month(year, month)


def main() -> None:
    """Read year and month, then display the calendar."""
    year = int(input("Enter year (e.g., 2024): "))
    month = int(input("Enter month (1-12): "))

    if not 1 <= month <= 12:
        print("Invalid month. Please enter a value between 1 and 12.")
        return

    print(f"\n{display_month_calendar(year, month)}")


if __name__ == "__main__":
    main()
