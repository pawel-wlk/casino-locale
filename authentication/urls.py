from django.urls import path
from .views import SignUpView, TestView

urlpatterns = [
    path("signup/", SignUpView, name="signup"),
    path("", TestView, name="test"),
]
