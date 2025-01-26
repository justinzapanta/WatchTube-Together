from rest_framework import serializers
from .. import models
from django.contrib.auth.models import User

class ChatRoomSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.ChatRoom
        fields = '__all__'


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['username', 'first_name']

class UserProfileSerializer(serializers.ModelSerializer):
    user_auth_credential = UserSerializer()
    class Meta:
        model = models.UserProfile
        fields = '__all__'