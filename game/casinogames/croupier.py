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
        self.counter = 0
        # self.init_game()


    def is_ready(self):
        return len(self.players) > 0 and all([player.ready for player in self.players])


    def add_player(self, player):
        if self.is_ready():
            return False
        self.players.append(player)
        return True


    def player_ready(self, channel_name):
        res = [player for player in self.players if player.channel_name == channel_name]
        if len(res) == 0:
            return

        res[0].ready = True
        if res[0].status == 'waiting' and self.is_ready():
            self.init_game()


    @abstractmethod
    def init_game(self):
        pass


    # croupier does his job here
    # after that calls update() on some players that send info to channels
    
    @abstractmethod
    def process_move(self, channel_name, move):
        pass
        