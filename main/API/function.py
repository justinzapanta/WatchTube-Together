import random
from ..models import User, UserProfile, Friend

def generate_code():
    characters = 'abcdefghijklmnopqrstuvwxyz1234567890'
    code = ''

    for num in range(6):
        index = random.randint(0, (len(characters) - 1))
        code += characters[index]
    return code



def add_friend(username, sender_username):
    user = User.objects.filter(username = username)
    sender = User.objects.filter(username = sender_username)

    if user and sender:
        sender_profile = UserProfile.objects.get(user_auth_credential = sender[0])

        in_friends = Friend.objects.filter(host = user[0], friend_info = sender_profile)

        if not in_friends:
            new_friend = Friend(
                host = user[0],
                friend_info = sender_profile
            )
            new_friend.save()

            return new_friend
        return False
    