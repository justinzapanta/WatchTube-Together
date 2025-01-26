from channels.generic.websocket import WebsocketConsumer
from asgiref.sync import async_to_sync
from .models import Room, UserProfile
from django.contrib.auth.models import User
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
                    'data' : {
                        'username' : data['username'],
                        'room_code' : data['room_code']
                    }
                }
            )
        elif data['action'] == 'message':
            async_to_sync(self.channel_layer.group_send)(
                self.roon_name,
                {
                    'type' : 'send_message',
                    'data' : data
                }
            )
        elif data['action'] == 'change_video':
            async_to_sync(self.channel_layer.group_send)(
                self.roon_name,
                {
                    'type' : 'change_video',
                    'video_id' : data['video_id']
                }
            )
        elif data['action'] == 'friend_request':
            async_to_sync(self.channel_layer.group_send)(
                self.roon_name,
                {
                    'type' : 'friend_request',
                    'data' : data
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


    #types
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
        data = event['data']
        room = Room.objects.filter(room_code = data['room_code'])
        user_profile = User.objects.get(username = data['username'])
        user = UserProfile.objects.get(user_auth_credential = user_profile)

        visitors = room[0].room_visitor
        is_unique = True
        for result in visitors['result']:
            if data['username'] == result['username']:
                is_unique = False
                break
        
        if is_unique:
            visitors['result'].append({
                'username' : data['username'],
                'user_image' : user.user_picture,
                'role' : 'visitor'
            })

            room.update(
                room_visitor = visitors
            )

        self.send(text_data=json.dumps({
            'action' : 'new_visitor',
            'user' : data['username']
        }))
    

    def send_message(self, event):
        info = event['data']

        self.send(text_data=json.dumps({
            'action' : 'message',
            'sender' : info['sender'],
            'message' : info['message']
        }))


    def change_video(self, event):
        video_id = event['video_id']

        self.send(text_data=json.dumps({
            'action' : 'change_video',
            'video_id' : video_id
        }))
    

    def friend_request(self, event):
        data = event['data']

        self.send(text_data=json.dumps({
            'action' : 'friend_reqeust',
            'user' : data['user'],
            'sender' : data['sender']
        }))