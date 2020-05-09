from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from ..player import Player


class BlackjackPlayer(Player):

    def __init__(self, username, channel_name):
        super().__init__(username, channel_name)
        self.status = 'waiting'


    def update(self, game_data):
        channel_layer = get_channel_layer()
        async_to_sync(channel_layer.send)(self.channel_name, {"type": "notify", "message": game_data, 'sender': self.name})
