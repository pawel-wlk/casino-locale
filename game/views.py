from django.shortcuts import render, redirect
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
def room(request, room_name):
    if room_name not in consumers.current_games:
        return redirect('index')

    return render(
        request, "game/room.html", {"room_name": room_name,
                                    "nav_links": nav_links, }
    )

@login_required(login_url="/login")
def create_room(request):
    if request.method != "POST":
        return redirect("index")

    game_type = request.POST['type']
    name = request.POST['roomName']

    if name in consumers.current_games:
        print("room already exists")
        return redirect("index")

    consumers.current_games[name] = consumers.defaultRoom()
    consumers.current_games[name]['room_type'] = game_type

    return redirect(f"/game/{name}")

