import json
from channels.generic.websocket import JsonWebsocketConsumer
from channels.consumer import AsyncConsumer
from asgiref.sync import async_to_sync
from collections import defaultdict
from .casinogames.croupier import Croupier
from .casinogames.player import Player
from .casinogames.blackjack.blackjack_croupier import BlackjackCroupier
from .casinogames.blackjack.blackjack_player import BlackjackPlayer
from .models import current_games
from .casinogames.blackjack.blackjack_bot import BlackjackBot
import re
import time

class GameRoomConsumer(JsonWebsocketConsumer):
    def join_room(self):
        async_to_sync(self.channel_layer.group_add)(
            self.room_name,
            self.channel_name
        )

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

        if current_games[self.room_name]['room_type']:
            self.croupier = BlackjackCroupier.get_instance(self.room_name)

        player = BlackjackPlayer(self.user.username, self.channel_name)
        self.croupier.add_player(player)

        current_games[self.room_name]['player_count'] += 1

        self.accept()

    def disconnect(self, close_code):
        self.close()
        current_games[self.room_name]['player_count'] -= 1

        if current_games[self.room_name]['player_count'] == 0:
            del self.croupier.instances[self.room_name]
            del current_games[self.room_name]
        else:
            self.croupier.delete_player(self.channel_name)
        self.leave_room()

    # receive_json is before chat_message

    def receive_json(self, json_data):
        message = json_data['message']

        if json_data['type'] == 'move':
            self.croupier.process_move(self.channel_name, message)
        elif json_data['type'] == 'init':
            print(f'{self.user.username} is ready')
            self.croupier.player_ready(self.channel_name)
        elif json_data['type'] == 'config':
            if message['action'] == 'add_bot' and self.croupier.status == 'waiting':
                print([p.name for p in self.croupier.players])
                num_of_bots = len(
                    [p.name for p in self.croupier.players if re.search('^bot.*', p.name)])
                t = int(round(time.time() * 1000))
                bot_name = f'bot{num_of_bots + 1}_{hex(t)[2:]}'
                self.croupier.add_player(BlackjackBot(
                    bot_name, bot_name, 2, self.croupier))
                print(f'Bot added: {bot_name}')
        else:

            self.room_send(
                {
                    # this field's value corresponds to the name of the method that will be called
                    'type': 'chat_message',
                    'message': message,
                    'sender': self.user.username
                }
            )

    def notify(self, event):
        message = event['message']
        sender = event['sender']
        # print(event)
        print(f"{self.user.username} was notified: {message}")
        self.send_json({'message': message, 'sender': sender})

    def chat_message(self, event):
        message = event['message']
        sender = event['sender']

        self.send_json({'message': message, 'sender': sender})
