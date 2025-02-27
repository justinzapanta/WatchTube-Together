from django.urls import re_path
from . import consumers

websocket_urlpatterns = [
    re_path(r'^ws/room/(?P<room_name>\w+)/$', consumers.YoutubePlayer.as_asgi()),
    re_path(r'^ws/global/$', consumers.HomeWebsocket.as_asgi()),
]