from django.db import models

# Create your models here.


def defaultRoom():
    return {
        'room_type': "",
        'player_count': 0,
        'pending': False,
    }


current_games = {}
