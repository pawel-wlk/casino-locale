from abc import abstractmethod
from .deck import Deck, Card, Hand

from ..models import current_games


class Croupier:
    instances = {}

    @classmethod
    def get_instance(cls, room_name):
        if room_name in Croupier.instances:
            return Croupier.instances[room_name]

        Croupier.instances[room_name] = cls(room_name)
        return Croupier.instances[room_name]

    
    def __init__(self, room_name):
        self.players = []
        self.deck = Deck()
        self.table_cards = Hand()
        self.status = 'waiting'
        self.pot = 0
        self.room_name = room_name
        # self.init_game()


    def is_ready(self):
        return len(self.players) > 0 and all([player.ready for player in self.players])


    def add_player(self, player):
        if self.is_ready():
            return False
        self.players.append(player)
        return True


    def delete_player(self, channel_name):
        res = [player for player in self.players if player.channel_name == channel_name]
        if len(res) == 0:
            return

        deleted_player = res[0]
        self.players.remove(deleted_player)

        if len(self.players) == 0:
            return

        if deleted_player.his_turn:
            self.next_turn()


    def player_ready(self, channel_name):
        res = [player for player in self.players if player.channel_name == channel_name]
        if len(res) == 0:
            return

        res[0].ready = True
        if res[0].status == 'waiting' and self.is_ready():
            current_games[self.room_name]['pending'] == True
            self.init_game()


    def next_turn(self):
        search_res = [i for i, p in enumerate(self.players) if p.his_turn]
        if len(search_res) == 0:
            self.players[0].his_turn = True
            return

        i = search_res[0]
        self.players[i].his_turn = False
        self.players[(i + 1) % len(self.players)].his_turn = True


    @abstractmethod
    def init_game(self):
        pass


    # croupier does his job here
    # after that calls update() on some players that send info to channels
    
    @abstractmethod
    def process_move(self, channel_name, move):
        pass
        