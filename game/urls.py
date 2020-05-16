from django.urls import path

from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('create', views.create_room, name='create'),
    path('<str:room_type>/<str:room_name>/', views.room, name='room')
]
