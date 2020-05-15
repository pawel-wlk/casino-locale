from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from authentication.views import nav_links

from . import consumers


@login_required(login_url="/login")
def index(request):
    return render(request, 'game/index.html', {
        'rooms': consumers.current_games.items,
        "nav_links": nav_links
    })


@login_required(login_url="/login")
def room(request, room_type, room_name):
    return render(
        request, "game/room.html", {"room_name": room_name,
                                    "room_type": room_type,
                                    "nav_links": nav_links, }
    )
