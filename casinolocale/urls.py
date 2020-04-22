from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path("admin/", admin.site.urls),
    path("game/", include("game.urls")),
    path("", include("django.contrib.auth.urls")),
    path("", include("authentication.urls")),
]
