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
        elif data['action'] == 'kick':
            async_to_sync(self.channel_layer.group_send)(
                self.roon_name,
                {
                    'type' : 'kick',
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
            'message' : info['message'],
            'sender_email' : info['sender_email']
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
            'sender' : data['sender'],
            'sender_name' : data['sender_name']
        }))

    
    def kick(self, event):
        data = event['data']



class HomeWebsocket(WebsocketConsumer):
    def connect(self):
        self.room = 'all'
        self.user = self.scope['user']
        self.accept()

        async_to_sync(self.channel_layer.group_add)(
            self.room,
            self.channel_name
        )


    def disconnect(self, code):
        async_to_sync(self.channel_layer.group_discard)(
            self.room,
            self.channel_name
        )

        async_to_sync(self.channel_layer.group_send)(
            self.room,
            {
                'type' : 'is_offline',
                'username' : self.user.username
            }
        )

    
    def receive(self, text_data=None):
        data = json.loads(text_data)

        if 'status' in data:
            if data['status'] == 'Online':
                #create a semder
                async_to_sync(self.channel_layer.group_send)(
                    self.room,
                    {
                        'type' : 'is_online',
                        'data' : data
                    }
                )

            
        elif data['action'] == 'invite':
            async_to_sync(self.channel_layer.group_send)(
                self.room,
                {
                    'type' : 'send_invitation',
                    'data' : data
                }
            )



    def is_online(self, event): 
        data = event['data']

        self.send(text_data=json.dumps({
            'action' : 'status',
            'status' : 'Online',
            'username' : data['username']
        }))

        user = User.objects.get(username = data['username'])
        user_profile = UserProfile.objects.filter(user_auth_credential = user).update(
            user_status = 'Online'            
        )


    def is_offline(self, event):
        username = event['username']

        self.send(text_data=json.dumps({
            'action' : 'status',
            'status' : 'Offline',
            'username' : username
        }))

        user = User.objects.get(username = username)
        user_profile = UserProfile.objects.filter(user_auth_credential = user).update(
            user_status = 'Offline'            
        )

    
    def send_invitation(self, event):
        data = event['data']
        print('prevent')
        self.send(text_data=json.dumps({
            'action' : 'invitation',
            'username' : data['username'],
            'link' : data['link']
        }))

    
