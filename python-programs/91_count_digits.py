"""Program 91: Count the Number of Digits Present In a Number

Demonstrates counting the digits of an integer using different approaches.

Reference: https://www.programiz.com/python-programming/examples/count-number-digits
"""


def count_digits_string(num: int) -> int:
    """Count digits by converting to a string."""
    return len(str(abs(num)))


def count_digits_loop(num: int) -> int:
    """Count digits mathematically using a loop."""
    if num == 0:
        return 1
    count = 0
    num = abs(num)
    while num > 0:
        num //= 10
        count += 1
    return count


def main() -> None:
    """Read a number and count its digits."""
    try:
        num_str = input("Enter an integer: ")
        num = int(num_str)
        
        count_str = count_digits_string(num)
        count_loop = count_digits_loop(num)
        
        print(f"\nNumber: {num}")
        print(f"Digits (string method): {count_str}")
        print(f"Digits (loop method):   {count_loop}")
        
        assert count_str == count_loop
        
    except ValueError:
        print("Invalid input. Please enter an integer.")


if __name__ == "__main__":
    main()
