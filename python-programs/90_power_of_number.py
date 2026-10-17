"""Program 90: Compute the Power of a Number

Computes base^exponent using different methods.

Reference: https://www.programiz.com/python-programming/examples/power
"""


def power_loop(base: float, exponent: int) -> float:
    """Compute base^exponent using a loop (for non-negative integer exponents)."""
    if exponent < 0:
        return 1 / power_loop(base, -exponent)
    result = 1
    for _ in range(exponent):
        result *= base
    return result


def power_recursive(base: float, exponent: int) -> float:
    """Compute base^exponent using recursion."""
    if exponent == 0:
        return 1
    if exponent < 0:
        return 1 / power_recursive(base, -exponent)
    return base * power_recursive(base, exponent - 1)


def main() -> None:
    """Read base and exponent, then compute the power."""
    base = float(input("Enter base: "))
    exponent = int(input("Enter exponent: "))

    # Method 1: Using ** operator
    result1 = base ** exponent
    print(f"\n{base} ^ {exponent}:")
    print(f"  Using ** operator: {result1}")

    # Method 2: Using pow()
    result2 = pow(base, exponent)
    print(f"  Using pow():       {result2}")

    # Method 3: Using loop
    result3 = power_loop(base, exponent)
    print(f"  Using loop:        {result3}")

    # Method 4: Using recursion
    result4 = power_recursive(base, exponent)
    print(f"  Using recursion:   {result4}")


if __name__ == "__main__":
    main()
