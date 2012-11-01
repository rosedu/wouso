import json
import array
import random
from datetime import datetime
from django_socketio import broadcast_channel, NoSocket
from wouso.core.user.models import Player
from wouso.interface.activity.models import Activity
from wouso.interface.activity.signals import addedActivity
from wouso.interface.chat.models import ChatUser, ChatMessage

def add_message(text, sender, to_room, user_to, mess_type, comand):
    """ content, author, room, user_to, mess_type, command """

    time_stamp = datetime.now()

    #TODO: Putem renunta la spam:) este inutil.
    difference_in_seconds = 1
    # sau>>
    #diff = time_stamp - sender.last_message_ts
    #difference_in_seconds = (diff.microseconds + (diff.seconds + diff.days * 24 * 3600) * 10**6) / 10**6

    if sender.has_modifier('block-communication'):
        return False
    if difference_in_seconds > 0.5:
        if sender.has_modifier('block-messages'):
            text = change_text(text)
        msg = ChatMessage(content=text, author=sender, dest_room=to_room, time_stamp=time_stamp,
            dest_user = user_to, mess_type=mess_type, comand=comand)
        msg.save()
    else:
        raise ValueError('Spam')

def create_message(user, query):
    """
    Common method for serve_message and some_old_message.
    Iterate through messages query and save only those messages that
    are normal or special, but for me.
    """
    msgs = []
    for message in query:
        if (message.dest_user == user and message.mess_type == "special") or message.mess_type == "normal":
            msgs.append(message.to_dict())
        else:
            continue
    return msgs

def new_activity_messages(chat_user):
    """
    Return a list of new messages from the activity module, formatted the same as create_message.
    """
    query = Activity.get_global_activity().filter(timestamp__gt=chat_user.last_message_ts)
    msgs = []
    for m in query:
        message = u'<strong>%s</strong> %s' % (m.user_from.nickname, m.message)
        msgs.append(dict(room='global', text=message, time=m.timestamp.strftime("%H:%M"), mess_type='activity'))
    return msgs

def serve_message(user, time_stamp):
    """
    Will return all messages that wasn't already delivered.
    Used when you write a new message or when you get a KeepAlive.
    """
    if time_stamp == 'null':
        query = ChatMessage.objects.filter(time_stamp__gt=user.last_message_ts, dest_room__participants=user)
        obj = {'user': unicode(user)}
        obj['count'] = query.count()
        obj['msgs'] = create_message(user, query)
        obj['time'] = str(datetime.now())
        user.last_message_ts = datetime.now()
        user.save()
        return obj
    else:
        query = ChatMessage.objects.filter(time_stamp__gt=time_stamp, dest_room__participants=user)

    messages = create_message(user, query) + new_activity_messages(user)

    if not messages:
        return None

    user.last_message_ts = datetime.now()
    user.save()

    obj = {'user': unicode(user)}
    obj['count'] = len(messages)
    obj['msgs'] = messages
    obj['time'] = str(datetime.now())
    return obj

def some_old_message(user, room, position):
    """
    Will return last 10 message from position for a specific room.
    Used on private chats, when you want to see some old messages.
    """
    number = int(position)
    query = ChatMessage.objects.filter(dest_room=room)
    query = query[len(query)-number-10:] if len(query) > (10 + number) else query

    number_query = 10 if len(query) == 0 else len(query) - number

    if not query:
        return None

    obj = {'user': unicode(user)}
    obj['count'] = number_query
    obj['msgs'] = create_message(user, query)

    return obj

def shuffle_text(text):
    if isinstance(text, unicode):
        temp = array.array('u', text)
        converter = temp.tounicode
    else:
        temp = array.array('c', text)
        converter = temp.tostring
    random.shuffle(temp)
    return converter()

def change_text(text):
    """
    Used on block_messages spell.
    Get a text and shuffle there words and there letter.
    """
    text = text.split(" ")
    random.shuffle(text)
    new_text = ""
    for world in text:
        if len(world) > 3:
            new_text = new_text + world[0] + shuffle_text(world[1:len(world)-1]) + world[len(world)-1] + " "
        else:
            new_text = new_text + world + " "
    return new_text

def get_author(request):
    return request.user.get_profile().get_extension(ChatUser)

def get_author_by_message(message):
    try:
        return Player.objects.get(pk=message['user']).get_extension(ChatUser)
    except Player.DoesNotExist:
        return None

def make_message(text, type, room):
    return {'action': 'message', 'mess_type': type, 'room': room, 'text': text, 'time': datetime.now().strftime("%H:%M")}

def broadcast_activity_handler(sender, **kwargs):
    """ Callback function for addedActivity signal
    It receives the activity newly added and sends it to global chat
    """
    a = kwargs.get('activity', None)
    if not a or not a.public:
        return

    message = u'<strong>%s</strong> %s' % (a.user_from.nickname, a.message)
    msg = dict(room='global', text=message, time=a.timestamp.strftime("%H:%M"), mess_type='activity', action='message')
    try:
        broadcast_channel(msg, 'global')
    except NoSocket:
        pass # fail silently

addedActivity.connect(broadcast_activity_handler)