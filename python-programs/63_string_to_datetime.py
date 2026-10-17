"""Program 63: Convert String to Datetime

Demonstrates converting date/time strings to datetime objects and formatting.

Reference: https://www.programiz.com/python-programming/examples/string-to-datetime
"""

from datetime import datetime


def string_to_datetime(date_string: str, fmt: str) -> datetime:
    """Parse a date string into a datetime object."""
    return datetime.strptime(date_string, fmt)


def datetime_to_string(dt: datetime, fmt: str) -> str:
    """Format a datetime object as a string."""
    return dt.strftime(fmt)


def main() -> None:
    """Demonstrate string-to-datetime conversions."""
    # Example 1: Common date format
    date_str = "21 June, 2018"
    dt = string_to_datetime(date_str, "%d %B, %Y")
    print(f"String: '{date_str}'")
    print(f"Parsed: {dt}")
    print(f"Type:   {type(dt)}\n")

    # Example 2: ISO format
    iso_str = "2024-03-15T14:30:00"
    dt2 = datetime.fromisoformat(iso_str)
    print(f"ISO String: '{iso_str}'")
    print(f"Parsed:     {dt2}\n")

    # Example 3: Format datetime back to string
    now = datetime.now()
    formats = {
        "%Y-%m-%d": "ISO date",
        "%d/%m/%Y": "DD/MM/YYYY",
        "%B %d, %Y": "Month Day, Year",
        "%I:%M %p": "12-hour time",
        "%A, %B %d, %Y %H:%M:%S": "Full datetime",
    }

    print(f"Current datetime: {now}\n")
    for fmt, description in formats.items():
        print(f"  {description:20s}: {datetime_to_string(now, fmt)}")


if __name__ == "__main__":
    main()
