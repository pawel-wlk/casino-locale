from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from authentication.views import nav_links


@login_required(login_url="/login")
def index(request):
    return render(request, "game/index.html", {"nav_links": nav_links})


@login_required(login_url="/login")
def room(request, room_name):
    return render(
        request, "game/room.html", {"room_name": room_name, "nav_links": nav_links,}
    )
