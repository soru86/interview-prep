"""Program 89: Reverse a Number

Reverses the digits of an integer (e.g., 12345 → 54321).

Reference: https://www.programiz.com/python-programming/examples/reverse-a-number
"""


def reverse_number_loop(num: int) -> int:
    """Reverse a number using a loop."""
    negative = num < 0
    num = abs(num)
    reversed_num = 0

    while num > 0:
        digit = num % 10
        reversed_num = reversed_num * 10 + digit
        num //= 10

    return -reversed_num if negative else reversed_num


def reverse_number_string(num: int) -> int:
    """Reverse a number using string conversion."""
    s = str(abs(num))
    reversed_s = s[::-1]
    result = int(reversed_s)
    return -result if num < 0 else result


def main() -> None:
    """Read a number and display its reverse."""
    num = int(input("Enter a number: "))

    reversed_loop = reverse_number_loop(num)
    reversed_str = reverse_number_string(num)

    print(f"Reversed (loop):   {reversed_loop}")
    print(f"Reversed (string): {reversed_str}")

    assert reversed_loop == reversed_str


if __name__ == "__main__":
    main()
