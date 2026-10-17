"""Program 42: Illustrate Different Set Operations

Demonstrates union, intersection, difference, and symmetric difference on sets.

Reference: https://www.programiz.com/python-programming/examples/set-operation
"""


def demonstrate_set_operations(set_a: set, set_b: set) -> dict[str, set]:
    """Perform and return results of all basic set operations."""
    return {
        "Union (A | B)": set_a | set_b,
        "Intersection (A & B)": set_a & set_b,
        "Difference (A - B)": set_a - set_b,
        "Difference (B - A)": set_b - set_a,
        "Symmetric Difference (A ^ B)": set_a ^ set_b,
    }


def main() -> None:
    """Demonstrate set operations with sample sets."""
    set_a = {1, 2, 3, 4, 5}
    set_b = {4, 5, 6, 7, 8}

    print(f"Set A: {set_a}")
    print(f"Set B: {set_b}")
    print("-" * 40)

    results = demonstrate_set_operations(set_a, set_b)

    for operation, result in results.items():
        print(f"  {operation}: {result}")

    # Additional checks
    print(f"\n  Is A subset of B?   {set_a.issubset(set_b)}")
    print(f"  Is A superset of B? {set_a.issuperset(set_b)}")


if __name__ == "__main__":
    main()
