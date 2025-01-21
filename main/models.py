from django.db import models
from django.contrib.auth.models import User
import uuid
# Create your models here.

class UserProfile(models.Model):
    user_uuid = models.UUIDField(default=uuid.uuid4, primary_key=True, null=False, unique=True, editable=False )
    user_auth_credential = models.ForeignKey(User, on_delete=models.CASCADE)
    user_picture = models.TextField()
    user_status = models.CharField(max_length=50, default='Online')


class Room(models.Model):
    room_uuid = models.UUIDField(default=uuid.uuid4, primary_key=True, null=False, unique=True, editable=False )
    room_code = models.CharField(max_length=40, null=True, default='')
    room_video_id = models.CharField(max_length=250, null=True, default='')
    room_owner = models.ForeignKey(UserProfile, on_delete=models.CASCADE)
    room_visitor = models.JSONField(null=True)


class Friend(models.Model):
    friend_uuid = models.UUIDField(default=uuid.uuid4, primary_key=True, null=False, unique=True, editable=False )
    friend_info = models.ForeignKey(UserProfile, on_delete=models.CASCADE)
