"""Program 20: Find Armstrong Numbers in an Interval

Finds all Armstrong (narcissistic) numbers within a given range.

Reference: https://www.programiz.com/python-programming/examples/armstrong-interval
"""


def is_armstrong(num: int) -> bool:
    """Return True if num is an Armstrong number."""
    digits = str(num)
    power = len(digits)
    return sum(int(d) ** power for d in digits) == num


def armstrong_numbers_in_interval(lower: int, upper: int) -> list[int]:
    """Return all Armstrong numbers in the interval [lower, upper]."""
    return [n for n in range(lower, upper + 1) if is_armstrong(n)]


def main() -> None:
    """Read an interval and display all Armstrong numbers within it."""
    lower = int(input("Enter lower bound: "))
    upper = int(input("Enter upper bound: "))

    results = armstrong_numbers_in_interval(lower, upper)

    print(f"\nArmstrong numbers between {lower} and {upper}:")
    if results:
        print(", ".join(map(str, results)))
    else:
        print("No Armstrong numbers found in this interval.")


if __name__ == "__main__":
    main()
