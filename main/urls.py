from django.urls import path
from . import views
from .API import api

urlpatterns= [
    path('', views.home, name='home'),
    path('room/<str:code>/', views.room, name='room'),
    path('room/<str:code>/<str:video_id>/', views.room, name='room'),
    path('sign-in/', views.sign_in, name='sign-in'),
    path('sign-up/', views.sign_up, name='sign-up'),
    path('<str:search>/', views.search_result, name='search'),

    #API
    path('api/room', api.room, name='api-room'),
    path('api/videos', api.videos, name='api-videos'),
    path('api/room/visitor', api.visitor, name='visitor'),
    path('api/messages', api.messages, name='api-messages')
]