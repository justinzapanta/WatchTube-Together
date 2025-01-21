from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate
from .API.youtube_api import YoutubeAPI
from .models import Room
# Create your views here.

def home(request):
    if request.method == 'POST':
        if request.POST['search'] != '':
            return redirect('search', str(request.POST['search']).strip())

    youtube = YoutubeAPI()
    recommendation_list = youtube.recommended()
    return render(request, 'main/views/home.html', {'recommendations' : recommendation_list})


def search_result(request, search):
    youtube = YoutubeAPI()
    results = youtube.search(search)
    return render(request, 'main/views/search.html', { 'results' : results})


def room(request, code, video_id=False):
    if request.user.is_authenticated:
        data = {}
        room = Room.objects.filter(room_code = code)
        if room:
            return render(request, 'main/views/room.html', {'room' : room, 'video_id' : video_id})
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