from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, logout
from .forms import SignUpForm
from .models import UserProfile

nav_links = [
    {"url": "/game/", "description": "Games"},
    {"url": "/logout/", "description": "Logout"},
]


def SignUpView(request):
    if request.method == "POST":
        form = SignUpForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get("username")
            raw_password = form.cleaned_data.get("password1")
            user = authenticate(username=username, password=raw_password)
            login(request, user)
            return redirect("/")
    else:
        form = SignUpForm()
    return render(request, "registration/signup.html", {"form": form})


def TestView(request):
    if request.user.is_authenticated:
        return render(
            request,
            "test.html",
            {
                "username": request.user.get_username(),
                "coins": UserProfile.objects.get(user=request.user).coins,
                "nav_links": nav_links,
            },
        )
    else:
        return redirect("login/")
