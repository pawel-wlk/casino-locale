from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from ..player import Player
from ..deck import Rank

class BlackjackPlayer(Player):

    def hand_sum(self):
        hand_sum = 0
        for card in self.hand:
            if card.suit in (Rank.JACK, Rank.QUEEN, Rank.KING):
                hand_sum += 10
            else:
                hand_sum += int(card.rank)
        return hand_sum

    def update(self, game_data):
        # pass
        channel_layer = get_channel_layer()
        if game_data['to'] == 'all':
            async_to_sync(channel_layer.group_send)(list(channel_layer.groups)[0], {"type": "notify", "message":game_data['hand'], "sender": game_data['player']})
