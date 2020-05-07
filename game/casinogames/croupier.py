from abc import abstractmethod
from .deck import Deck, Card, Suit, Rank


class Croupier:
    instances = {}

    @classmethod
    def get_instance(cls, room_name):
        if room_name in Croupier.instances:
            return Croupier.instances[room_name]

        Croupier.instances[room_name] = cls()
        return Croupier.instances[room_name]

    
    def __init__(self):
        self.players = []
        self.deck = Deck()
        self.table_cards = []
        self.init_game()

    def add_player(self, player):
        self.players.append(player)


    @abstractmethod
    def init_game(self):
        pass

    
    # croupier does his job here
    # after that calls update() on some players that send info to channels
    
    @abstractmethod
    def process_move(self, channel_name, move):
        pass
