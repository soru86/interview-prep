"""Program 10: Check if a Number is Positive, Negative or 0

Demonstrates conditional statements to classify a number.

Reference: https://www.programiz.com/python-programming/examples/positive-negative-zero
"""


def classify_number(num: float) -> str:
    """Classify a number as positive, negative, or zero.

    Args:
        num: The number to classify.

    Returns:
        A string describing the classification.
    """
    if num > 0:
        return "positive"
    elif num < 0:
        return "negative"
    else:
        return "zero"


def main() -> None:
    """Read a number and display its classification."""
    num = float(input("Enter a number: "))

    result = classify_number(num)
    print(f"The number {num} is {result}")


if __name__ == "__main__":
    main()
