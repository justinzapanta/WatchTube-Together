from urllib import response
from rest_framework.response import Response
from rest_framework.decorators import api_view
from .function import generate_code, add_friend
from ..models import Room, UserProfile, ChatRoom, Friend
from .serializer import ChatRoomSerializer, UserProfileSerializer
from .youtube_api import YoutubeAPI
from django.contrib.auth.models import User

@api_view(['POST', 'GET', 'PUT'])
def room(request):
    if request.user.is_authenticated:
        code = generate_code()
        user = UserProfile.objects.get(user_auth_credential = request.user)
        room = Room.objects.filter(room_owner = user)

        if request.method == 'GET':
            if request.query_params:
                code = request.query_params['code']
                room = Room.objects.filter(room_code = code)
                if room:                        
                    return Response({'result' : {
                        'room_code' : room[0].room_code,
                        'video_id' : room[0].room_video_id
                    }})
                return Response({'result' : 'Invalid Code'})

        elif request.method == 'POST':
            if request.data.get('create'):
                if room:
                    chat_room = ChatRoom.objects.filter(chat_room = room[0]).delete()
                    id = ''
                    if request.data.get('video_id'):
                        id = request.data['video_id']
                        
                    room.update(
                        room_video_id = id,
                        room_code = code,
                        room_visitor = {'result' : [{
                            'username' : request.user.username,
                            'user_image' : user.user_picture,
                            'role' : 'owner'
                        }]},
                    )

                    return Response({'result' : {
                        'room_code' : room[0].room_code,
                        'room_video_id' : room[0].room_video_id
                    }})
                
        elif request.method == 'PUT':
            if room:
                room.update(room_video_id = request.data['video_id'])
                return Response({'result' : {
                    'room_code' : room[0].room_code,
                    'room_video_id' : room[0].room_video_id
                }})
    return Response({'result' : 'error'})


@api_view(['GET'])
def videos(request):
    youtube = YoutubeAPI()
    if request.method == 'GET':
        if request.query_params:
            return Response({'result' : youtube.search(request.query_params['search'])})

    return Response({'result' : 'error'})


@api_view(['PUT', 'GET'])
def visitor(request):
    if request.user.is_authenticated:
        if request.method == 'PUT':
            if request.data:
                room = Room.objects.get(room_code = request.data['room_code'])
                visitors = room.room_visitor

                for index, result in enumerate(visitors['result']):
                    if request.data['user'] in result.values() and result['role'] == 'visitor':
                        del visitors['result'][index]
                        break

                room.room_visitor = visitors
                room.save()

                return Response({'result' : room.room_visitor})
        elif request.method == 'GET':
            if request.query_params:
                room = Room.objects.filter(room_code = request.query_params['code'])

                return Response({'result' : room[0].room_visitor})
    return Response({'result' : 'error'})



@api_view(['POST', 'PUT'])
def messages(request):
    if request.user.is_authenticated:
        data = request.data
        if request.method == 'POST':
            room = Room.objects.filter(room_code = data['chat_code'])

            if room:
                data = request.data
                message = ChatRoom(
                    chat_room = room[0],
                    chat_sender = data['chat_sender'],
                    chat_message = data['chat_message']
                )
                message.save()

    return Response({'result' : 'error'})



@api_view(['POST', 'GET', 'update'])
def user_profile(request):
    if request.user.is_authenticated:
        if request.method == 'GET':
            data = request.query_params
            user = User.objects.get(username = data['username'])
            user_info = UserProfile.objects.filter(user_auth_credential = user)

            if user_info:
                return Response({'result' : UserProfileSerializer(user_info, many=True).data})
    
    return Response({'result' : 'error'}, status=500)



@api_view(['POST', 'GET'])
def friends(request):
    if request.user.is_authenticated:
        if request.data:
            data = request.data

            if request.method == 'POST':
                print(request.user.username, data)
                new_friend = add_friend(request.user.username, data['sender']) #for user
                new_sender = add_friend(data['sender'], request.user.username) #for sender

                if new_friend:
                    return Response({'result', 'success'}, status=200)
                
    return Response({'result' : 'error'}, status=500)