
from django.utils.html import strip_tags
from django_socketio import events
from wouso.interface.chat.utils import  change_text, get_author, serve_message, some_old_message, add_message, create_message
from datetime import datetime, timedelta
from models import *

@events.on_message(channel="global")
def message(request, socket, context, message):
    """
    Event handler for a room receiving a message. First validates a
    joining user's name and sends them the list of users.

    if data['opcode'] == 'message':
        room = roomexist(data['room'])
        if user.user.has_perm('chat.super_chat_user'):
            if data['msg'][0] == '/' and data['room'] == 'global':
                text = data['msg'].split(" ")
                if len(text) > 1:
                    try:
                        sender = Player.objects.get(nickname=text[1])
                        sender = sender.user.get_profile().get_extension(ChatUser)
                    except:
                        return json_response(serve_message(user, time_stamp))

                    if text[0] == '/kick':
                        add_message(text[1], user, room, sender, "special", "kick")
                    if text[0] == '/unban':
                        sender.can_access_chat = True
                        sender.save()
                    if text[0] == '/ban':
                        sender.can_access_chat = False
                        sender.save()
                    return json_response(serve_message(user, time_stamp))

    """
    user = get_author(request)
    data = message
    #time_stamp = data['time']
    #if time_stamp == 'null':
    #    return json_response(serve_message(user, time_stamp))

    room = roomexist(data['room'])
    if message["action"] == "message":
        message["msg"] = strip_tags(message["msg"])
        message["name"] = unicode(user)
        socket.send_and_broadcast_channel(message)


    print data


def json_response(object):
    return HttpResponse(simplejson.dumps(object))

def roomexist(room_name):
    try:
        return ChatRoom.objects.get(name = room_name)
    except ChatRoom.DoesNotExist:
        return None