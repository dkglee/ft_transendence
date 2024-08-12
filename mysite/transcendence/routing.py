from django.urls import re_path, include
from transcendence.consumer import GameConsumer

# the empty string routes to TranscendenceConsumer, which manages the chat functionality.
websocket_urlpatterns = [
	re_path(r'ws/game/(?P<session_id>\w+)/$', GameConsumer.as_asgi()),
]
