from abc import abstractmethod


class Player:
    def __init__(self, name):
        self.name = name
        self.hand = []
        self.game_data = {} # TO-DO

    @abstractmethod
    def update(self, game_data):
        pass
