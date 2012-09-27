import array
import random
from wouso.interface.chat.models import ChatUser, ChatMessage
from datetime import datetime

def add_message(text, sender, toRoom, user_to, messType, comand):
    """ content, author, room, user_to, messType, command """

    timeStamp = datetime.now()

    #TODO: Putem renunta la spam:) este inutil.
    difference_in_seconds = 1
    # sau>>
    #diff = timeStamp - sender.lastMessageTS
    #difference_in_seconds = (diff.microseconds + (diff.seconds + diff.days * 24 * 3600) * 10**6) / 10**6

    if sender.has_modifier('block-communication'):
        return False
    if difference_in_seconds > 0.5:
        if sender.has_modifier('block-messages'):
            text = change_text(text)
        msg = ChatMessage(content=text, author=sender, destRoom=toRoom, timeStamp=timeStamp,
            destUser = user_to, messType=messType, comand=comand)
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
        if (message.destUser == user and message.messType == "special") or message.messType == "normal":
            msgs.append(message.to_dict())
        else:
            continue
    return msgs

def serve_message(user, timeStamp):
    """
    Will return all messages that wasn't already delivered.
    Used when you write a new message or when you get a KeepAlive.
    """
    if timeStamp == 'null':
        print "xx"
        timeStamp = datetime.now()
        query = ChatMessage.objects.filter(timeStamp__gt=user.lastMessageTS, destRoom__participants=user)
        obj = {'user': unicode(user)}
        obj['count'] = query.count()
        obj['msgs'] = create_message(user, query)
        obj['time'] = str(datetime.now())
        user.lastMessageTS = datetime.now()
        user.save()
        return obj
    else:
        query = ChatMessage.objects.filter(timeStamp__gt=timeStamp, destRoom__participants=user)

    if not query:
        return None

    user.lastMessageTS = datetime.now()
    user.save()

    obj = {'user': unicode(user)}
    obj['count'] = query.count()
    obj['msgs'] = create_message(user, query)
    obj['time'] = str(datetime.now())
    return obj

def some_old_message(user, room, position):
    """
    Will return last 10 message from position for a specific room.
    Used on private chats, when you want to see some old messages.
    """
    number = int(position)
    query = ChatMessage.objects.filter(destRoom=room)
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