from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from ..player import Player
from ..deck import Hand


class BlackjackPlayer(Player):

    def __init__(self, username, channel_name):
        super().__init__(username, channel_name)
        self.status = 'waiting'
        self.first_hand = self.hand
        self.second_hand = Hand()
        self.splitted = False
        self.doubled = False


    def update(self, game_data):
        channel_layer = get_channel_layer()
        async_to_sync(channel_layer.send)(self.channel_name, {"type": "notify", "message": game_data, 'sender': self.name})


    def calc_available_moves(self):
        if self.status == 'waiting':
            self.available_moves = ['get_ready']
            return self.available_moves

        if not self.his_turn:
            self.available_moves = []
            return []

        self.available_moves = ['stand']
        if self.status == 'betting':
            self.available_moves.append('bet')
        elif self.status == 'playing':
            self.available_moves.append('hit')
            if len(self.hand.cards) == 2:
                self.available_moves.append('double')
            if not self.splitted and len(self.hand.cards) == 2 and (self.hand.cards[0]).rank == (self.hand.cards[1]).rank:
                self.available_moves.append('split')

        return self.available_moves