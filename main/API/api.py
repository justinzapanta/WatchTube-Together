from urllib import response
from rest_framework.response import Response
from rest_framework.decorators import api_view
from .function import generate_code
from ..models import Room, UserProfile
from .youtube_api import YoutubeAPI

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
                    room_visitors = room[0].room_visitor

                    in_visitor = False
                    for visitor in room_visitors['result']:
                        if visitor['username'] == request.user.username:
                            in_visitor = True

                    if not in_visitor:
                        room_visitors['result'].append({
                            'username' : request.user.username,
                            'user_image' : user.user_picture,
                            'role' : 'visitor'
                        })
                        room.update(
                            room_visitor = room_visitors
                        )
                        
                    return Response({'result' : {
                        'room_code' : room[0].room_code,
                        'video_id' : room[0].room_video_id
                    }})
                return Response({'result' : 'Invalid Code'})

        elif request.method == 'POST':
            if request.data.get('create'):
                if room:
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
                room = Room.objects.get(room_code = request.query_params['code'])

                print(room)
                return Response({'result' : room.room_visitor})

    return Response({'result' : 'error'})