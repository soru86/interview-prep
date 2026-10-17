"""Program 23: Find Numbers Divisible by Another Number

Uses list comprehension and filter() to find numbers in a list
that are divisible by a given divisor.

Reference: https://www.programiz.com/python-programming/examples/number-divisible
"""


def find_divisible(numbers: list[int], divisor: int) -> list[int]:
    """Return numbers from the list that are divisible by divisor."""
    return [n for n in numbers if n % divisor == 0]


def find_divisible_filter(numbers: list[int], divisor: int) -> list[int]:
    """Return numbers divisible by divisor using filter()."""
    return list(filter(lambda x: x % divisor == 0, numbers))


def main() -> None:
    """Demonstrate finding numbers divisible by a given number."""
    numbers = [19, 65, 57, 39, 152, 639, 121, 44, 90, 190]
    divisor = 13

    result = find_divisible(numbers, divisor)

    print(f"Original list: {numbers}")
    print(f"Divisor: {divisor}")
    print(f"Numbers divisible by {divisor}: {result}")


if __name__ == "__main__":
    main()
