
from datetime import datetime
from django.utils.html import strip_tags
from django_socketio import events
from wouso.interface.chat.utils import get_author, add_message
from models import *

@events.on_message(channel="global")
def message(request, socket, context, message):
    """
    Event handler for a room receiving a message. First validates a
    joining user's name and sends them the list of users.
    """
    user = get_author(request)
    room = get_room_or_none(message['room'])
    if user.user.has_perm("chat.super_chat_user"):
        if message['msg'][0] == '/' and message['room'] == "global":
            text = message['msg'].split(" ")
            if len(text) > 1:
                try:
                    sender = Player.objects.get(nickname=text[1])
                    sender = sender.user.get_profile().get_extension(ChatUser)
                except:
                    return False

                if text[0] == "/kick":
                    add_message(text[1], user, room, sender, "special", "kick")
                elif text[0] == "/unban":
                    sender.can_access_chat = True
                    sender.save()
                elif text[0] == "/ban":
                    sender.can_access_chat = False
                    sender.save()
                else:
                    return False
                message['text'] = strip_tags(text[1])
                message['user'] = unicode(user.nickname)
                message['time'] = str(datetime.now().strftime('%H:%M'))
                message['command'] = "kick"
                message['mess_type'] = "special"
                message['dest_user'] = unicode(sender.nickname)
                socket.send_and_broadcast_channel(message)
                return False

    if message['action'] == "message":
        add_message(message['msg'], user, room, user, "normal", "normal")
        message['text'] = strip_tags(message['msg'])
        message['user'] = unicode(user.nickname)
        message['time'] = str(datetime.now().strftime('%H:%M'))
        message['command'] = "normal"
        message['mess_type'] = "normal"
        message['dest_user'] = unicode(user.nickname)
        socket.send_and_broadcast_channel(message)

def get_room_or_none(room_name):
    try:
        return ChatRoom.objects.get(name = room_name)
    except ChatRoom.DoesNotExist:
        return None