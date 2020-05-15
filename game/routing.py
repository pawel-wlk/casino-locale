from django.urls import re_path

from . import consumers

websocket_url_patterns = [
    re_path(r'ws/room/(?P<room_type>\w+)/(?P<room_name>\w+)/$', consumers.GameRoomConsumer)
]