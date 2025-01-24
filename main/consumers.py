from channels.generic.websocket import WebsocketConsumer
from asgiref.sync import async_to_sync
from .models import Room, UserProfile
import json


class YoutubePlayer(WebsocketConsumer):
    def connect(self):
        self.roon_name = self.scope['url_route']['kwargs']['room_name']

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
                'data' : 'leave'
            }
        )
        print('disconnected', code)


    def receive(self, text_data):
        data = json.loads(text_data)
        
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
                'action' : 'leave',
                'data' : room[0].room_visitor
            }))