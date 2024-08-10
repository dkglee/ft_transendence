from django.urls import path, include
from transcendence.consumer import TranscendenceConsumer

# the empty string routes to TranscendenceConsumer, which manages the chat functionality.
websocket_urlpatterns = [
    path("", TranscendenceConsumer.as_asgi()),
]
