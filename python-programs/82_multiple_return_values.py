"""Program 82: Return Multiple Values From a Function

Demonstrates returning multiple values from a function using tuples,
dictionaries, namedtuples, and dataclasses.

Reference: https://www.programiz.com/python-programming/examples/multiple-return-values
"""

from collections import namedtuple
from dataclasses import dataclass


def return_tuple(name: str, age: int) -> tuple[str, int, str]:
    """Return multiple values as a tuple."""
    greeting = f"Hello, {name}!"
    return name, age, greeting


def return_dict(name: str, age: int) -> dict:
    """Return multiple values as a dictionary."""
    return {"name": name, "age": age, "greeting": f"Hello, {name}!"}


# Using namedtuple
PersonInfo = namedtuple("PersonInfo", ["name", "age", "greeting"])


def return_namedtuple(name: str, age: int) -> PersonInfo:
    """Return multiple values as a namedtuple."""
    return PersonInfo(name=name, age=age, greeting=f"Hello, {name}!")


# Using dataclass
@dataclass
class PersonData:
    """A dataclass for person data."""
    name: str
    age: int
    greeting: str


def return_dataclass(name: str, age: int) -> PersonData:
    """Return multiple values as a dataclass."""
    return PersonData(name=name, age=age, greeting=f"Hello, {name}!")


def main() -> None:
    """Demonstrate returning multiple values."""
    # Method 1: Tuple unpacking
    name, age, greeting = return_tuple("Alice", 30)
    print(f"Tuple:      name={name}, age={age}, greeting={greeting}")

    # Method 2: Dictionary
    result = return_dict("Bob", 25)
    print(f"Dict:       name={result['name']}, age={result['age']}")

    # Method 3: Namedtuple
    info = return_namedtuple("Charlie", 35)
    print(f"Namedtuple: name={info.name}, age={info.age}")

    # Method 4: Dataclass
    data = return_dataclass("Diana", 28)
    print(f"Dataclass:  name={data.name}, age={data.age}")


if __name__ == "__main__":
    main()
