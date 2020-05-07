import json
from channels.generic.websocket import JsonWebsocketConsumer
from channels.consumer import AsyncConsumer
from asgiref.sync import async_to_sync
from collections import defaultdict
from .casinogames.croupier import Croupier
from .casinogames.player import Player


current_games = defaultdict(int)


class GameRoomConsumer(JsonWebsocketConsumer):
    def join_room(self):
        async_to_sync(self.channel_layer.group_add)(
            self.room_name,
            self.channel_name
        )
        self.croupier = Croupier.get_instance(self.room_name)

    def leave_room(self):
        async_to_sync(self.channel_layer.group_discard)(
            self.room_name,
            self.channel_name
        )

    def room_send(self, data):
        async_to_sync(self.channel_layer.group_send)(self.room_name, data)

    def connect(self):
        self.user = self.scope['user']

        if self.user.is_anonymous:
            return

        self.room_name = self.scope['url_route']['kwargs']['room_name']

        self.join_room()

        player = Player(self.user.username, self.channel_name)
        self.croupier.add_player(player)

        current_games[self.room_name] += 1

        self.accept()

    def disconnect(self, close_code):
        self.close()
        current_games[self.room_name] -= 1

        self.leave_room()

    # receive_json is before chat_message

    def receive_json(self, json_data):
        message = json_data['message']

        self.room_send(
            {
                # this field's value corresponds to the name of the method that will be called
                'type': 'chat_message',
                'message': message,
                'sender': self.user.username
            }
        )

        if json_data['type'] == 'move':
            self.croupier.process_move(self.channel_name, message)

    def chat_message(self, event):
        message = event['message']
        sender = event['sender']

        self.send_json({'message': message, 'sender': sender})
