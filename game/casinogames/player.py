from abc import abstractmethod
from .deck import Hand


class Player:
    def __init__(self, username, channel_name):
        self.name = username
        self.channel_name = channel_name
        self.hand = Hand()
        self.game_data = {} # TO-DO
        self.ready = False


    # update game -> send info to channels
    # schema: 
    #   channel_layer = get_channel_layer()
    #   async_to_sync(channel_layer.group_send)(list(channel_layer_groups)[0], {message_to_send //type, message, sender, etc //})
    # sender is {self.name}
    # @abstractmethod
    def update(self, game_data):
        pass
      