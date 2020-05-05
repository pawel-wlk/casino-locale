import json
from channels.generic.websocket import JsonWebsocketConsumer
from channels.consumer import AsyncConsumer
from asgiref.sync import async_to_sync
from collections import defaultdict

current_games = defaultdict(int)


class GameRoomConsumer(JsonWebsocketConsumer):
    def create_room(self):
        async_to_sync(self.channel_layer.group_add)(
            self.room_name,
            self.channel_name
        )

    def delete_room(self):
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

        if current_games[self.room_name] == 0:
            self.create_room()

        current_games[self.room_name] += 1

        self.accept()

    def disconnect(self, close_code):
        self.close()
        current_games[self.room_name] -= 1

        if current_games[self.room_name] == 0:
            self.delete_room()

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

    def chat_message(self, event):
        message = event['message']
        sender = event['sender']

        self.send_json({'message': message, 'sender': sender})
