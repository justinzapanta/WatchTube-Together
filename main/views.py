from pickle import TRUE
from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, logout
from .API.youtube_api import YoutubeAPI
from .models import Room, UserProfile, ChatRoom, Friend
from django.contrib.auth.models import User
import json
# Create your views here.

def home(request):
    data = {}

    if request.user.is_authenticated:
        friends = Friend.objects.filter(host=request.user)
        profile = UserProfile.objects.get(user_auth_credential = request.user)
        data['profile_picture'] = profile.user_picture
        data['friends'] = friends
        data['username'] = request.user.username
        
    if request.method == 'POST':
        if request.POST['search'] != '':
            return redirect('search', str(request.POST['search']).strip())

    youtube = YoutubeAPI()
    recommendation_list = youtube.recommended()
    data['recommendations'] = recommendation_list

    return render(request, 'main/views/home.html', data) #


def search_result(request, search):
    youtube = YoutubeAPI()
    results = youtube.search(search)
    return render(request, 'main/views/search.html', { 'results' : results})
    


def room(request, code, video_id=False):
    if request.user.is_authenticated:
        room = Room.objects.filter(room_code = code)

        if room:
            chat_room = ChatRoom.objects.filter(chat_room = room[0])

            data = {
                'room' : room[0], 
                'video_id' : video_id,
                'room_code' : code,
                'visitors' : room[0].room_visitor,
                'messages' : chat_room,
                'user_name' : request.user.first_name
            }

            if request.user.username == room[0].room_owner.user_auth_credential.username:
                data['owner'] = 'yes'
            return render(request, 'main/views/room.html', data)
        else:
            return redirect('home')
    else:
        return redirect('sign-in')


def sign_in(request):
    data = {}
    if not request.user.is_authenticated:
        if request.method == 'POST':
            user = authenticate(username = request.POST['username'], password = request.POST['password'])
            if user:
                login(request, user)
                return redirect('home')
            else:
                data['notif'] = 'Invalid email or password'
        return render(request, 'main/views/login.html', data)
    return redirect('home')



def sign_up(request):
    if not request.user.is_authenticated:
        data = {}
        if request.method == 'POST':
            email_exist = User.objects.filter(username = request.POST['email'])
            
            if not email_exist:
                new_user = User.objects.create_user(
                    username = request.POST['email'],
                    password = request.POST['password'],
                    first_name = request.POST['username']
                )
                
                new_userProfile = UserProfile(
                    user_auth_credential = new_user,
                    user_picture = 'https://cdn0.iconfinder.com/data/icons/people-57/24/user-circle-1024.png',
                    user_status = 'Online'
                )
                new_userProfile.save()

                new_userRoom = Room(
                    room_code = '12349^#$@!',
                    room_video_id = '1234',
                    room_owner = new_userProfile,
                    room_visitor = json.dumps({"" : ""})
                )
                new_userRoom.save()

                login(request, new_user)
                return redirect('home')
            
            data['notif'] = 'This email is taken'
        return render(request, 'main/views/register.html', data)
    return redirect('home')


def sign_out(request):
    user = UserProfile.objects.filter(user_auth_credential = request.user)
    user.update(
        user_status = 'Offline'
    )

    logout(request)
    return redirect('sign-in')