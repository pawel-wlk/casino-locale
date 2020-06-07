from .blackjack_player import BlackjackPlayer
from ..deck import Rank
from dataclasses import dataclass
import math
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from collections import Counter


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

    def compare(self, hand_sum):
        if self.points == 8 and hand_sum <= self.points:
            return True
        if self.points == 17 and hand_sum >= self.points:
            return True
        return self.points == hand_sum


class BlackjackBot(BlackjackPlayer):
    def __init__(self, username, channel_name, decks, croupier, balance=0):
        super().__init__(username, channel_name, balance)
        self.strategy = Strategy(decks)
        self.croupier = croupier
        self.ready = True

    def update(self, game_data):
        self.strategy.update(game_data)
        if self.his_turn and game_data['game_status'] == 'betting':
            self.make_bet(game_data)
        elif self.his_turn and game_data['game_status'] == 'playing':
            self.make_move(game_data)

    def send(self, move):
        self.croupier.process_move(self.channel_name, move)

    def make_bet(self, game_data):
        move = {'action': 'bet', 'value': 100}
        self.send(move)

    def make_move(self, game_data):
        croupier_hand = [Rank[c['rank']]
                         for c in game_data['croupier']['hand']]
        player = [p for p in game_data['players']
                  if p['player'] == self.name][0]
        player_hand = [Rank[c['rank']] for c in player['hand'][player['current_hand']]]
        player_hand_sum = player['sum']
        next_move = self.strategy.next_move(
            croupier_hand[0], player_hand, player_hand_sum, self.splitted)
        if next_move not in self.available_moves:
            next_move = 'stand'
        self.send({'action': next_move})


class Strategy:
    def update(self, game_data):
        cards = [Rank[c['rank']] for player in game_data['players']
                 for hand in player['hand'] for c in hand]
        cards += [Rank[c['rank']] for c in game_data['croupier']['hand']]

        # If there aren't any seen cards, the game has just started
        # and we need to analyze all cards.
        # Otherwise we need to analyze only the difference.
        if len(self.cards_seen) > 0:
            c1 = Counter(cards)
            c2 = Counter(self.cards_seen)
            cards = list((c1 - c2).elements())

        for c in cards:
            if c in [Rank.TWO, Rank.THREE, Rank.FOUR, Rank.FIVE, Rank.SIX]:
                self.curr_value += 1
            elif c in [Rank.TEN, Rank.ACE, Rank.KING, Rank.QUEEN, Rank.JACK]:
                self.curr_value -= 1

        self.cards_left -= len(cards)
        decks_left = math.ceil((self.cards_left - 1) /
                               52) if self.cards_left // 52 > 0 else 1
        self.real_value = self.curr_value / decks_left
        self.cards_seen = cards

    def next_move(self, croupier_card, player_hand, hand_sum, splitted):
        print(player_hand, hand_sum)
        # First check if it is a pair or a hand with an ace
        if len(player_hand) == 2:
            hand = set(player_hand)
            # Multiple splits are not allowed
            if len(hand) > 1 or not splitted:
                search_res = [row for row in self.moves if row.cards == hand]
                if len(search_res) > 0:
                    return self.extract_move(search_res[0].moves[croupier_card])

        # Analyze only the value of the hand
        search_res = [row for row in self.moves if row.compare(hand_sum)]
        if len(search_res) > 0:
            return self.extract_move(search_res[0].moves[croupier_card])

        return 'stand'

    def extract_move(self, move):
        # If there is no extra move, return only the basic one
        if move.extra_move == '':
            return move.basic_move

        # Negative sign before the value means that every number smaller than it
        # should be accepted. Non-negative value means that every number greater than it
        # should be accepted
        sign = math.copysign(1, move.value)
        compare = lambda x: x >= move.value
        if sign < 0:
            compare = lambda x: x >= move.value

        if compare(self.real_value):
            return move.extra_move
        else:
            return move.basic_move

    def __init__(self, decks):
        self.cards_left = decks * 52
        self.cards_seen = []
        self.curr_value = 0
        self.real_value = 0
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
                            Rank.SIX: Move(0, 'stand', ''), Rank.SEVEN: Move(0, 'stand', ''),
                            Rank.EIGHT: Move(0, 'stand', ''), Rank.NINE: Move(0, 'stand', ''),
                            Rank.TEN: Move(0, 'stand', ''), Rank.JACK: Move(0, 'stand', ''),
                            Rank.QUEEN: Move(0, 'stand', ''), Rank.KING: Move(0, 'stand', ''),
                            Rank.ACE: Move(0, 'stand', '')
            }
            ),
            PlayerCards({Rank.ACE, Rank.TWO}, 0,
                        {
                            Rank.TWO: Move(0, 'hit', ''), Rank.THREE: Move(0, 'hit', ''),
                            Rank.FOUR: Move(3, 'hit', 'double'), Rank.FIVE: Move(-0.0, 'double', 'hit'),
                            Rank.SIX: Move(-2, 'double', 'hit'), Rank.SEVEN: Move(0, 'hit', ''),
                            Rank.EIGHT: Move(0, 'hit', ''), Rank.NINE: Move(0, 'hit', ''),
                            Rank.TEN: Move(0, 'hit', ''), Rank.JACK: Move(0, 'hit', ''),
                            Rank.QUEEN: Move(0, 'hit', ''), Rank.KING: Move(0, 'hit', ''),
                            Rank.ACE: Move(0, 'hit', '')
            }
            ),
            PlayerCards({Rank.ACE, Rank.THREE}, 0,
                        {
                            Rank.TWO: Move(0, 'hit', ''), Rank.THREE: Move(0, 'hit', ''),
                            Rank.FOUR: Move(1, 'hit', 'double'), Rank.FIVE: Move(-2, 'double', 'hit'),
                            Rank.SIX: Move(-5, 'double', 'hit'), Rank.SEVEN: Move(0, 'hit', ''),
                            Rank.EIGHT: Move(0, 'hit', ''), Rank.NINE: Move(0, 'hit', ''),
                            Rank.TEN: Move(0, 'hit', ''), Rank.JACK: Move(0, 'hit', ''),
                            Rank.QUEEN: Move(0, 'hit', ''), Rank.KING: Move(0, 'hit', ''),
                            Rank.ACE: Move(0, 'hit', '')
            }
            ),
            PlayerCards({Rank.ACE, Rank.FOUR}, 0,
                        {
                            Rank.TWO: Move(0, 'hit', ''), Rank.THREE: Move(0, 'hit', ''),
                            Rank.FOUR: Move(-1, 'double', 'hit'), Rank.FIVE: Move(-5, 'double', 'hit'),
                            Rank.SIX: Move(0, 'double', ''), Rank.SEVEN: Move(0, 'hit', ''),
                            Rank.EIGHT: Move(0, 'hit', ''), Rank.NINE: Move(0, 'hit', ''),
                            Rank.TEN: Move(0, 'hit', ''), Rank.JACK: Move(0, 'hit', ''),
                            Rank.QUEEN: Move(0, 'hit', ''), Rank.KING: Move(0, 'hit', ''),
                            Rank.ACE: Move(0, 'hit', '')
            }
            ),
            PlayerCards({Rank.ACE, Rank.FIVE}, 0,
                        {
                            Rank.TWO: Move(0, 'hit', ''), Rank.THREE: Move(4, 'hit', 'double'),
                            Rank.FOUR: Move(-3, 'double', 'hit'), Rank.FIVE: Move(0, 'double', ''),
                            Rank.SIX: Move(0, 'double', ''), Rank.SEVEN: Move(0, 'hit', ''),
                            Rank.EIGHT: Move(0, 'hit', ''), Rank.NINE: Move(0, 'hit', ''),
                            Rank.TEN: Move(0, 'hit', ''), Rank.JACK: Move(0, 'hit', ''),
                            Rank.QUEEN: Move(0, 'hit', ''), Rank.KING: Move(0, 'hit', ''),
                            Rank.ACE: Move(0, 'hit', '')
            }
            ),
            PlayerCards({Rank.ACE, Rank.SIX}, 0,
                        {
                            Rank.TWO: Move(1, 'hit', 'double'), Rank.THREE: Move(-4, 'double', 'hit'),
                            Rank.FOUR: Move(0, 'double', ''), Rank.FIVE: Move(0, 'double', ''),
                            Rank.SIX: Move(0, 'double', ''), Rank.SEVEN: Move(0, 'hit', ''),
                            Rank.EIGHT: Move(0, 'hit', ''), Rank.NINE: Move(0, 'hit', ''),
                            Rank.TEN: Move(0, 'hit', ''), Rank.JACK: Move(0, 'hit', ''),
                            Rank.QUEEN: Move(0, 'hit', ''), Rank.KING: Move(0, 'hit', ''),
                            Rank.ACE: Move(0, 'hit', '')
            }
            ),
            PlayerCards({Rank.ACE, Rank.SEVEN}, 0,
                        {
                            Rank.TWO: Move(0, 'stand', ''), Rank.THREE: Move(-3, 'double', 'hit'),
                            Rank.FOUR: Move(0, 'double', ''), Rank.FIVE: Move(0, 'double', ''),
                            Rank.SIX: Move(0, 'double', ''), Rank.SEVEN: Move(0, 'stand', ''),
                            Rank.EIGHT: Move(0, 'stand', ''), Rank.NINE: Move(0, 'hit', ''),
                            Rank.TEN: Move(0, 'hit', ''), Rank.JACK: Move(0, 'hit', ''),
                            Rank.QUEEN: Move(0, 'hit', ''), Rank.KING: Move(0, 'hit', ''),
                            Rank.ACE: Move(0, 'hit', '')
            }
            ),
            PlayerCards({Rank.ACE, Rank.EIGHT}, 0,
                        {
                            Rank.TWO: Move(0, 'stand', ''), Rank.THREE: Move(0, 'stand', ''),
                            Rank.FOUR: Move(0, 'stand', ''), Rank.FIVE: Move(0, 'stand', ''),
                            Rank.SIX: Move(0, 'stand', ''), Rank.SEVEN: Move(0, 'stand', ''),
                            Rank.EIGHT: Move(0, 'stand', ''), Rank.NINE: Move(0, 'stand', ''),
                            Rank.TEN: Move(0, 'stand', ''), Rank.JACK: Move(0, 'stand', ''),
                            Rank.QUEEN: Move(0, 'stand', ''), Rank.KING: Move(0, 'stand', ''),
                            Rank.ACE: Move(0, 'stand', '')
            }
            ),
            PlayerCards({Rank.ACE, Rank.NINE}, 0,
                        {
                            Rank.TWO: Move(0, 'stand', ''), Rank.THREE: Move(0, 'stand', ''),
                            Rank.FOUR: Move(0, 'stand', ''), Rank.FIVE: Move(0, 'stand', ''),
                            Rank.SIX: Move(0, 'stand', ''), Rank.SEVEN: Move(0, 'stand', ''),
                            Rank.EIGHT: Move(0, 'stand', ''), Rank.NINE: Move(0, 'stand', ''),
                            Rank.TEN: Move(0, 'stand', ''), Rank.JACK: Move(0, 'stand', ''),
                            Rank.QUEEN: Move(0, 'stand', ''), Rank.KING: Move(0, 'stand', ''),
                            Rank.ACE: Move(0, 'stand', '')
            }
            ),
            PlayerCards({Rank.ACE}, 0,
                        {
                            Rank.TWO: Move(0, 'split', ''), Rank.THREE: Move(0, 'split', ''),
                            Rank.FOUR: Move(0, 'split', ''), Rank.FIVE: Move(0, 'split', ''),
                            Rank.SIX: Move(0, 'split', ''), Rank.SEVEN: Move(0, 'split', ''),
                            Rank.EIGHT: Move(0, 'split', ''), Rank.NINE: Move(0, 'split', ''),
                            Rank.TEN: Move(0, 'split', ''), Rank.JACK: Move(0, 'split', ''),
                            Rank.QUEEN: Move(0, 'split', ''), Rank.KING: Move(0, 'split', ''),
                            Rank.ACE: Move(0, 'split', '')
            }
            ),
            PlayerCards({Rank.TWO}, 0,
                        {
                            Rank.TWO: Move(-4, 'split', 'hit'), Rank.THREE: Move(0, 'split', ''),
                            Rank.FOUR: Move(0, 'split', ''), Rank.FIVE: Move(0, 'split', ''),
                            Rank.SIX: Move(0, 'split', ''), Rank.SEVEN: Move(0, 'split', ''),
                            Rank.EIGHT: Move(0, 'hit', ''), Rank.NINE: Move(0, 'hit', ''),
                            Rank.TEN: Move(0, 'hit', ''), Rank.JACK: Move(0, 'hit', ''),
                            Rank.QUEEN: Move(0, 'hit', ''), Rank.KING: Move(0, 'hit', ''),
                            Rank.ACE: Move(0, 'hit', '')
            }
            ),
            PlayerCards({Rank.THREE}, 0,
                        {
                            Rank.TWO: Move(-0.0, 'split', 'hit'), Rank.THREE: Move(-5, 'split', 'hit'),
                            Rank.FOUR: Move(0, 'split', ''), Rank.FIVE: Move(0, 'split', ''),
                            Rank.SIX: Move(0, 'split', ''), Rank.SEVEN: Move(0, 'split', ''),
                            Rank.EIGHT: Move(4, 'hit', 'double'), Rank.NINE: Move(0, 'hit', ''),
                            Rank.TEN: Move(0, 'hit', ''), Rank.JACK: Move(0, 'hit', ''),
                            Rank.QUEEN: Move(0, 'hit', ''), Rank.KING: Move(0, 'hit', ''),
                            Rank.ACE: Move(0, 'hit', '')
            }
            ),
            PlayerCards({Rank.FOUR}, 0,
                        {
                            Rank.TWO: Move(0, 'hit', ''), Rank.THREE: Move(0, 'hit', ''),
                            Rank.FOUR: Move(1, 'hit', 'double'), Rank.FIVE: Move(-2, 'split', 'hit'),
                            Rank.SIX: Move(-5, 'split', 'hit'), Rank.SEVEN: Move(0, 'hit', ''),
                            Rank.EIGHT: Move(0, 'hit', ''), Rank.NINE: Move(0, 'hit', ''),
                            Rank.TEN: Move(0, 'hit', ''), Rank.JACK: Move(0, 'hit', ''),
                            Rank.QUEEN: Move(0, 'hit', ''), Rank.KING: Move(0, 'hit', ''),
                            Rank.ACE: Move(0, 'hit', '')
            }
            ),
            PlayerCards({Rank.FIVE}, 0,
                        {
                            Rank.TWO: Move(0, 'double', ''), Rank.THREE: Move(0, 'double', ''),
                            Rank.FOUR: Move(0, 'double', ''), Rank.FIVE: Move(0, 'double', ''),
                            Rank.SIX: Move(0, 'double', ''), Rank.SEVEN: Move(0, 'double', ''),
                            Rank.EIGHT: Move(-5, 'double', 'hit'), Rank.NINE: Move(-2, 'double', 'hit'),
                            Rank.TEN: Move(4, 'hit', 'double'), Rank.JACK: Move(4, 'hit', 'double'),
                            Rank.QUEEN: Move(4, 'hit', 'double'), Rank.KING: Move(4, 'hit', 'double'),
                            Rank.ACE: Move(1, 'hit', 'double')
            }
            ),
            PlayerCards({Rank.SIX}, 0,
                        {
                            Rank.TWO: Move(-2, 'split', 'hit'), Rank.THREE: Move(-2, 'split', 'hit'),
                            Rank.FOUR: Move(-5, 'split', 'hit'), Rank.FIVE: Move(0, 'split', ''),
                            Rank.SIX: Move(0, 'split', ''), Rank.SEVEN: Move(0, 'hit', ''),
                            Rank.EIGHT: Move(0, 'hit', ''), Rank.NINE: Move(0, 'hit', ''),
                            Rank.TEN: Move(0, 'hit', ''), Rank.JACK: Move(0, 'hit', ''),
                            Rank.QUEEN: Move(0, 'hit', ''), Rank.KING: Move(0, 'hit', ''),
                            Rank.ACE: Move(0, 'hit', '')
            }
            ),
            PlayerCards({Rank.SEVEN}, 0,
                        {
                            Rank.TWO: Move(0, 'split', ''), Rank.THREE: Move(0, 'split', ''),
                            Rank.FOUR: Move(0, 'split', ''), Rank.FIVE: Move(0, 'split', ''),
                            Rank.SIX: Move(0, 'split', ''), Rank.SEVEN: Move(0, 'split', ''),
                            Rank.EIGHT: Move(5, 'hit', 'double'), Rank.NINE: Move(0, 'hit', ''),
                            Rank.TEN: Move(0, 'hit', ''), Rank.JACK: Move(0, 'hit', ''),
                            Rank.QUEEN: Move(0, 'hit', ''), Rank.KING: Move(0, 'hit', ''),
                            Rank.ACE: Move(0, 'hit', '')
            }
            ),
            PlayerCards({Rank.EIGHT}, 0,
                        {
                            Rank.TWO: Move(0, 'split', ''), Rank.THREE: Move(0, 'split', ''),
                            Rank.FOUR: Move(0, 'split', ''), Rank.FIVE: Move(0, 'split', ''),
                            Rank.SIX: Move(0, 'split', ''), Rank.SEVEN: Move(0, 'split', ''),
                            Rank.EIGHT: Move(0, 'split', ''), Rank.NINE: Move(0, 'split', ''),
                            Rank.TEN: Move(0, 'split', ''), Rank.JACK: Move(0, 'split', ''),
                            Rank.QUEEN: Move(0, 'split', ''), Rank.KING: Move(0, 'split', ''),
                            Rank.ACE: Move(0, 'split', '')
            }
            ),
            PlayerCards({Rank.NINE}, 0,
                        {
                            Rank.TWO: Move(-3, 'split', 'hit'), Rank.THREE: Move(-4, 'hit', ''),
                            Rank.FOUR: Move(-6, 'split', 'hit'), Rank.FIVE: Move(0, 'split', ''),
                            Rank.SIX: Move(0, 'split', ''), Rank.SEVEN: Move(0, 'stand', ''),
                            Rank.EIGHT: Move(0, 'split', ''), Rank.NINE: Move(0, 'split', ''),
                            Rank.TEN: Move(0, 'stand', ''), Rank.JACK: Move(0, 'stand', ''),
                            Rank.QUEEN: Move(0, 'stand', ''), Rank.KING: Move(0, 'stand', ''),
                            Rank.ACE: Move(0, 'stand', '')
            }
            ),
            PlayerCards({Rank.TEN}, 0,
                        {
                            Rank.TWO: Move(0, 'stand', ''), Rank.THREE: Move(0, 'stand', ''),
                            Rank.FOUR: Move(6, 'stand', 'split'), Rank.FIVE: Move(5, 'stand', 'split'),
                            Rank.SIX: Move(4, 'stand', 'split'), Rank.SEVEN: Move(0, 'stand', ''),
                            Rank.EIGHT: Move(0, 'stand', ''), Rank.NINE: Move(0, 'stand', ''),
                            Rank.TEN: Move(0, 'stand', ''), Rank.JACK: Move(0, 'stand', ''),
                            Rank.QUEEN: Move(0, 'stand', ''), Rank.KING: Move(0, 'stand', ''),
                            Rank.ACE: Move(0, 'stand', '')
            }
            ),
            PlayerCards({Rank.QUEEN}, 0,
                        {
                            Rank.TWO: Move(0, 'stand', ''), Rank.THREE: Move(0, 'stand', ''),
                            Rank.FOUR: Move(6, 'stand', 'split'), Rank.FIVE: Move(5, 'stand', 'split'),
                            Rank.SIX: Move(4, 'stand', 'split'), Rank.SEVEN: Move(0, 'stand', ''),
                            Rank.EIGHT: Move(0, 'stand', ''), Rank.NINE: Move(0, 'stand', ''),
                            Rank.TEN: Move(0, 'stand', ''), Rank.JACK: Move(0, 'stand', ''),
                            Rank.QUEEN: Move(0, 'stand', ''), Rank.KING: Move(0, 'stand', ''),
                            Rank.ACE: Move(0, 'stand', '')
            }
            ),
            PlayerCards({Rank.KING}, 0,
                        {
                            Rank.TWO: Move(0, 'stand', ''), Rank.THREE: Move(0, 'stand', ''),
                            Rank.FOUR: Move(6, 'stand', 'split'), Rank.FIVE: Move(5, 'stand', 'split'),
                            Rank.SIX: Move(4, 'stand', 'split'), Rank.SEVEN: Move(0, 'stand', ''),
                            Rank.EIGHT: Move(0, 'stand', ''), Rank.NINE: Move(0, 'stand', ''),
                            Rank.TEN: Move(0, 'stand', ''), Rank.JACK: Move(0, 'stand', ''),
                            Rank.QUEEN: Move(0, 'stand', ''), Rank.KING: Move(0, 'stand', ''),
                            Rank.ACE: Move(0, 'stand', '')
            }
            ),
            PlayerCards({Rank.JACK}, 0,
                        {
                            Rank.TWO: Move(0, 'stand', ''), Rank.THREE: Move(0, 'stand', ''),
                            Rank.FOUR: Move(6, 'stand', 'split'), Rank.FIVE: Move(5, 'stand', 'split'),
                            Rank.SIX: Move(4, 'stand', 'split'), Rank.SEVEN: Move(0, 'stand', ''),
                            Rank.EIGHT: Move(0, 'stand', ''), Rank.NINE: Move(0, 'stand', ''),
                            Rank.TEN: Move(0, 'stand', ''), Rank.JACK: Move(0, 'stand', ''),
                            Rank.QUEEN: Move(0, 'stand', ''), Rank.KING: Move(0, 'stand', ''),
                            Rank.ACE: Move(0, 'stand', '')
            }
            ),
        ]
        self.moves = moves
