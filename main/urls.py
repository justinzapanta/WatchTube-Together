from django.urls import path
from . import views
from .API import api

urlpatterns= [
    path('', views.home, name='home'),
    path('room/<str:code>/', views.room, name='room'),
    path('room/<str:code>/<str:video_id>/', views.room, name='room'),
    path('sign-in/', views.sign_in, name='sign-in'),
    path('sign-up/', views.sign_up, name='sign-up'),
    path('sign-out/', views.sign_out, name='sign-out'),

    #API
    path('api/room', api.room, name='api-room'),
    path('api/videos', api.videos, name='api-videos'),
    path('api/room/visitor', api.visitor, name='visitor'),
    path('api/messages', api.messages, name='api-messages'),
    path('api/user-profile', api.user_profile, name='api-user_profile'),
    path('api/friends', api.friends, name='api-friend'),

    path('search/<str:search>/', views.search_result, name='search'),
]