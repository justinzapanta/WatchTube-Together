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
            pass

        elif request.method == 'POST':
            if request.data.get('create'):
                if room:
                    print(request.data)
                    id = ''
                    if request.data.get('video_id'):
                        id = request.data['video_id']
                        
                    room.update(
                        room_video_id = id,
                        room_code = code,
                        room_visitor = {'result' : {
                            'username' : request.user.username
                        }},
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