from enum import IntEnum, Enum
from dataclasses import dataclass
import random


class Suit(Enum):
    SPADES = 0
    CLUBS = 1
    DIAMONDS = 2
    HEARTS = 3


class Rank(IntEnum):
    ACE = 11
    TWO = 2
    THREE = 3
    FOUR = 4
    FIVE = 5
    SIX = 6
    SEVEN = 7
    EIGHT = 8
    NINE = 9
    TEN = 10
    JACK = 12
    QUEEN = 13
    KING = 14


@dataclass
class Card:
    suit: Suit
    rank: Rank


class Deck:
    def __init__(self):
        self.reset()


    def reset(self):
        self.cards = [Card(suit, rank) for suit in Suit for rank in Rank]
        random.shuffle(self.cards)


    def get_cards(self, count):
        return_cards = self.cards[:count]
        self.cards = self.cards[count:]
        return return_cards


class Hand:
    def __init__(self):
        self.cards = []


    def add_cards(self, new_cards):
        self.cards += new_cards

    
    def get_as_dict(self):
        return [{'suit': c.suit.name, 'rank': c.rank.name} for c in self.cards]