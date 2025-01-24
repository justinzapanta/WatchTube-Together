from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate
from .API.youtube_api import YoutubeAPI
from .models import Room, UserProfile
# Create your views here.

def home(request):
    data = {}

    if request.user.is_authenticated:
        profile = UserProfile.objects.get(user_auth_credential = request.user)
        data['profile_picture'] = profile.user_picture
        
    # if request.method == 'POST':
    #     if request.POST['search'] != '':
    #         return redirect('search', str(request.POST['search']).strip())

    # youtube = YoutubeAPI()
    # recommendation_list = youtube.recommended()
    return render(request, 'main/views/home.html', data) #{'recommendations' : recommendation_list}


def search_result(request, search):
    # youtube = YoutubeAPI()
    # results = youtube.search(search)
    # return render(request, 'main/views/search.html', { 'results' : results})
    pass


def room(request, code, video_id=False):
    if request.user.is_authenticated:
        room = Room.objects.filter(room_code = code)

        if room:
            data = {
                'room' : room, 
                'video_id' : video_id,
                'room_code' : code,
                'visitors' : room[0].room_visitor
            }

            if request.user.username == room[0].room_owner.user_auth_credential.username:
                data['owner'] = 'yes'
            return render(request, 'main/views/room.html', data)
        else:
            return redirect('home')
    else:
        return redirect('sign-in')


def sign_in(request):
    if request.user.is_authenticated:
        return redirect('home')
    else:
        if request.method == 'POST':
            user = authenticate(username = request.POST['username'], password = request.POST['password'])
            if user:
                login(request, user)
                return redirect('sign-in')
        return render(request, 'main/views/login.html')


def sign_up(request):
    return render(request, 'main/views/register.html')