from channels.generic.websocket import WebsocketConsumer
from asgiref.sync import async_to_sync
from .models import Room, UserProfile
import json


class YoutubePlayer(WebsocketConsumer):
    def connect(self):
        self.roon_name = self.scope['url_route']['kwargs']['room_name']
        self.user = self.scope['user']
        
        async_to_sync(self.channel_layer.group_add)(
            self.roon_name,
            self.channel_name
        )
        self.accept()

    def disconnect(self, code):
        async_to_sync(self.channel_layer.group_discard)(
            self.roon_name,
            self.channel_name
        )

        async_to_sync(self.channel_layer.group_send)(
            self.roon_name,
            {
                'type' : 'user_leave',
                'data' : ['leave', self.user.username],
            }
        )


    def receive(self, text_data):
        data = json.loads(text_data)
        
        if data['action'] == 'new_visitor':
            async_to_sync(self.channel_layer.group_send)(
                self.roon_name,
                {
                    'type' : 'new_visitor',
                    'user' : self.user.username
                }
            )
        else:
            async_to_sync(self.channel_layer.group_send)(
                self.roon_name,
                {
                    'type' : 'sync_video',
                    'data' : data
                }
            )


    def sync_video(self, event):
        data = event['data']

        self.send(text_data=json.dumps({
            'time' : data['time'],
            'action' : data['action']
        }))

    
    def user_leave(self, event):
        room = Room.objects.filter(room_code = self.roon_name)

        if room:
            self.send(text_data=json.dumps({
                'action' : event['data'][0],
                'data' : event['data'][1],
            }))

    
    def new_visitor(self, event):
        self.send(text_data=json.dumps({
            'action' : 'new_visitor',
            'user' : event['user']
        }))