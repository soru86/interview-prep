"""Program 30: Shuffle Deck of Cards

Demonstrates creating and shuffling a standard 52-card deck using
itertools.product and random.shuffle.

Reference: https://www.programiz.com/python-programming/examples/shuffle-card
"""

import itertools
import random


def create_deck() -> list[str]:
    """Create a standard 52-card deck."""
    suits = ["♠ Spades", "♥ Hearts", "♦ Diamonds", "♣ Clubs"]
    ranks = ["Ace", "2", "3", "4", "5", "6", "7", "8", "9", "10",
             "Jack", "Queen", "King"]
    return [f"{rank} of {suit}" for rank, suit in itertools.product(ranks, suits)]


def shuffle_deck(deck: list[str]) -> list[str]:
    """Return a shuffled copy of the deck."""
    shuffled = deck.copy()
    random.shuffle(shuffled)
    return shuffled


def main() -> None:
    """Create, shuffle, and display cards from a deck."""
    deck = create_deck()
    print(f"Deck created with {len(deck)} cards.\n")

    shuffled = shuffle_deck(deck)

    num_cards = 5
    print(f"Drawing {num_cards} cards from the shuffled deck:")
    for i, card in enumerate(shuffled[:num_cards], 1):
        print(f"  {i}. {card}")


if __name__ == "__main__":
    main()
