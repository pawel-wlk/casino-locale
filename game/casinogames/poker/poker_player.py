from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from ..player import Player


class PokerPlayer(Player):
    def __init__(self, username, channel_name):
        super().__init__(username, channel_name)
        self.status = "waiting"

    def update(self, game_data):
        channel_layer = get_channel_layer()
        async_to_sync(channel_layer.send)(
            self.channel_name,
            {"type": "notify", "message": game_data, "sender": self.name},
        )

    def calc_available_moves(self):
        if self.status == "waiting":
            self.available_moves = ["get_ready"]
            return self.available_moves

        if not self.his_turn:
            self.available_moves = []
            return []


        if self.status == "fold":
            return []

        if self.status == "additional_round":
            self.available_moves = ["fold", "call"]
            
        elif self.status == "first_round":
            self.available_moves = ["fold", "call", "raise"]

        elif self.status == "playing":
            self.available_moves = ["fold", "bet", "raise", "call", "check"]

        return self.available_moves
