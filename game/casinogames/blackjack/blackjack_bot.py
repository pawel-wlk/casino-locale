from .blackjack_player import BlackjackPlayer
from ..deck import Rank
from dataclasses import dataclass
import math


@dataclass
class Move:
    value: int
    basic_move: str
    extra_move: str


class PlayerCards:
    def __init__(self, cards, points, moves):
        self.cards = cards
        self.points = points
        self.moves = moves


class BlackjackBot(BlackjackPlayer):
    def __init__(self, username, channel_name, balance=0):
        super().__init__(username, channel_name, balance)
        self.strategy = Strategy()


class Strategy:
    def __init__(self):
        moves = [
            PlayerCards(set(), 8,
                        {
                            Rank.TWO: Move(0, 'hit', ''), Rank.THREE: Move(0, 'hit', ''), 
                            Rank.FOUR: Move(5, 'hit', 'double'), Rank.FIVE: Move(3, 'hit', 'double'), 
                            Rank.SIX: Move(1, 'hit', 'double'), Rank.SEVEN: Move(0, 'hit', ''),
                            Rank.EIGHT: Move(0, 'hit', ''), Rank.NINE: Move(0, 'hit', ''),
                            Rank.TEN: Move(0, 'hit', ''), Rank.JACK: Move(0, 'hit', ''),
                            Rank.QUEEN: Move(0, 'hit', ''), Rank.KING: Move(0, 'hit', ''),
                            Rank.ACE: Move(0, 'hit', '')
                        }
                        ),
            PlayerCards(set(), 9,
                        {
                            Rank.TWO: Move(1, 'hit', 'double'), Rank.THREE: Move(-1, 'double', 'hit'), 
                            Rank.FOUR: Move(-3, 'double', 'hit'), Rank.FIVE: Move(-5, 'double', 'hit'), 
                            Rank.SIX: Move(0, 'double', ''), Rank.SEVEN: Move(3, 'hit', 'double'),
                            Rank.EIGHT: Move(0, 'hit', ''), Rank.NINE: Move(0, 'hit', ''),
                            Rank.TEN: Move(0, 'hit', ''), Rank.JACK: Move(0, 'hit', ''),
                            Rank.QUEEN: Move(0, 'hit', ''), Rank.KING: Move(0, 'hit', ''),
                            Rank.ACE: Move(0, 'hit', '')
                        }
                        ),
            PlayerCards(set(), 10,
                        {
                            Rank.TWO: Move(0, 'double', ''), Rank.THREE: Move(0, 'double', ''), 
                            Rank.FOUR: Move(0, 'double', ''), Rank.FIVE: Move(0, 'double', ''), 
                            Rank.SIX: Move(0, 'double', ''), Rank.SEVEN: Move(0, 'double', ''),
                            Rank.EIGHT: Move(-5, 'double', 'hit'), Rank.NINE: Move(-2, 'double', 'hit'),
                            Rank.TEN: Move(4, 'hit', 'double'), Rank.JACK: Move(4, 'hit', 'double'),
                            Rank.QUEEN: Move(4, 'hit', 'double'), Rank.KING: Move(4, 'hit', 'double'),
                            Rank.ACE: Move(4, 'hit', 'double')
                        }
                        ),
            PlayerCards(set(), 11,
                        {
                            Rank.TWO: Move(0, 'double', ''), Rank.THREE: Move(0, 'double', ''), 
                            Rank.FOUR: Move(0, 'double', ''), Rank.FIVE: Move(0, 'double', ''), 
                            Rank.SIX: Move(0, 'double', ''), Rank.SEVEN: Move(0, 'double', ''),
                            Rank.EIGHT: Move(0, 'double', ''), Rank.NINE: Move(-5, 'double', 'hit'),
                            Rank.TEN: Move(-5, 'double', 'hit'), Rank.JACK: Move(-5, 'double', 'hit'),
                            Rank.QUEEN: Move(-5, 'double', 'hit'), Rank.KING: Move(-5, 'double', 'hit'),
                            Rank.ACE: Move(1, 'hit', 'double')
                        }
                        ),
            PlayerCards(set(), 12,
                        {
                            Rank.TWO: Move(3, 'hit', 'stand'), Rank.THREE: Move(2, 'hit', 'stand'), 
                            Rank.FOUR: Move(-0.0, 'stand', 'hit'), Rank.FIVE: Move(-2, 'stand', 'hit'), 
                            Rank.SIX: Move(-1, 'stand', 'hit'), Rank.SEVEN: Move(0, 'hit', ''),
                            Rank.EIGHT: Move(0, 'hit', ''), Rank.NINE: Move(0, 'hit', ''),
                            Rank.TEN: Move(0, 'hit', ''), Rank.JACK: Move(0, 'hit', ''),
                            Rank.QUEEN: Move(0, 'hit', ''), Rank.KING: Move(0, 'hit', ''),
                            Rank.ACE: Move(0, 'hit', '')
                        }
                        ),
            PlayerCards(set(), 13,
                        {
                            Rank.TWO: Move(-1, 'stand', 'hit'), Rank.THREE: Move(-2, 'stand', 'hit'), 
                            Rank.FOUR: Move(-4, 'stand', 'hit'), Rank.FIVE: Move(-5, 'stand', 'hit'), 
                            Rank.SIX: Move(-5, 'stand', 'hit'), Rank.SEVEN: Move(0, 'hit', ''),
                            Rank.EIGHT: Move(0, 'hit', ''), Rank.NINE: Move(0, 'hit', ''),
                            Rank.TEN: Move(0, 'hit', ''), Rank.JACK: Move(0, 'hit', ''),
                            Rank.QUEEN: Move(0, 'hit', ''), Rank.KING: Move(0, 'hit', ''),
                            Rank.ACE: Move(0, 'hit', '')
                        }
                        ),
            PlayerCards(set(), 14,
                        {
                            Rank.TWO: Move(-4, 'stand', 'hit'), Rank.THREE: Move(-5, 'stand', 'hit'), 
                            Rank.FOUR: Move(0, 'stand', ''), Rank.FIVE: Move(0, 'stand', ''), 
                            Rank.SIX: Move(0, 'stand', ''), Rank.SEVEN: Move(0, 'hit', ''),
                            Rank.EIGHT: Move(0, 'hit', ''), Rank.NINE: Move(0, 'hit', ''),
                            Rank.TEN: Move(0, 'hit', ''), Rank.JACK: Move(0, 'hit', ''),
                            Rank.QUEEN: Move(0, 'hit', ''), Rank.KING: Move(0, 'hit', ''),
                            Rank.ACE: Move(0, 'hit', '')
                        }
                        ),
            PlayerCards(set(), 15,
                        {
                            Rank.TWO: Move(0, 'stand', ''), Rank.THREE: Move(0, 'stand', ''), 
                            Rank.FOUR: Move(0, 'stand', ''), Rank.FIVE: Move(0, 'stand', ''), 
                            Rank.SIX: Move(0, 'stand', ''), Rank.SEVEN: Move(0, 'hit', ''),
                            Rank.EIGHT: Move(0, 'hit', ''), Rank.NINE: Move(0, 'hit', ''),
                            Rank.TEN: Move(4, 'hit', 'stand'), Rank.JACK: Move(4, 'hit', 'stand'),
                            Rank.QUEEN: Move(4, 'hit', 'stand'), Rank.KING: Move(4, 'hit', 'stand'),
                            Rank.ACE: Move(0, 'hit', '')
                        }
                        ),
            PlayerCards(set(), 16,
                        {
                            Rank.TWO: Move(0, 'stand', ''), Rank.THREE: Move(0, 'stand', ''), 
                            Rank.FOUR: Move(0, 'stand', ''), Rank.FIVE: Move(0, 'stand', ''), 
                            Rank.SIX: Move(0, 'stand', ''), Rank.SEVEN: Move(0, 'hit', ''),
                            Rank.EIGHT: Move(0, 'hit', ''), Rank.NINE: Move(5, 'hit', 'stand'),
                            Rank.TEN: Move(0, 'hit', 'stand'), Rank.JACK: Move(0, 'hit', 'stand'),
                            Rank.QUEEN: Move(0, 'hit', 'stand'), Rank.KING: Move(0, 'hit', 'stand'),
                            Rank.ACE: Move(0, 'hit', '')
                        }
                        ),
            PlayerCards(set(), 17,
                        {
                            Rank.TWO: Move(0, 'stand', ''), Rank.THREE: Move(0, 'stand', ''), 
                            Rank.FOUR: Move(0, 'stand', ''), Rank.FIVE: Move(0, 'stand', ''), 
                            Rank.SIX: Move(0, 'stand', ''), Rank.SEVEN: Move(0, 'hit', ''),
                            Rank.EIGHT: Move(0, 'stand', ''), Rank.NINE: Move(0, 'stand', ''),
                            Rank.TEN: Move(0, 'stand', ''), Rank.JACK: Move(0, 'stand', ''),
                            Rank.QUEEN: Move(0, 'stand', ''), Rank.KING: Move(0, 'stand', ''),
                            Rank.ACE: Move(0, 'stand', '')
                        }
                        ),
        ]
        self.moves = moves
