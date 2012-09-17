from datetime import datetime, timedelta
from django.core.urlresolvers import reverse
from django.http import HttpResponse, HttpResponseRedirect, HttpResponseBadRequest
from django.contrib.auth.decorators import login_required
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.utils import simplejson

from wouso.core.config.models import BoolSetting
from models import *
from wouso.interface.chat.utils import  change_text, get_author, serve_message, some_old_message, add_message

@login_required
def index(request):
    user = request.user.get_profile()
    chat_user = get_author(request)

    if user.has_modifier('block-global-chat-page') or user.has_modifier('block-communication') or not chat_user.canAccessChat:
        return HttpResponseRedirect(reverse('wouso.interface.views.homepage'))
    if BoolSetting.get('disable-Chat').get_value():
        return HttpResponseRedirect(reverse('wouso.interface.views.homepage'))

    return render_to_response('chat/chat.html',
                            {'chat_user': user,
                            },
                            context_instance=RequestContext(request))

@login_required
def archive(request):
    user = request.user.get_profile()
    chat_user = get_author(request)

    if user.has_modifier('block-global-chat-page') or user.has_modifier('block-communication') or not chat_user.canAccessChat:
        return HttpResponseRedirect(reverse('wouso.interface.views.homepage'))
    if BoolSetting.get('disable-Chat').get_value():
        return HttpResponseRedirect(reverse('wouso.interface.views.homepage'))

    return render_to_response('chat/archive.html',
            {'chat_user': user,
             },
        context_instance=RequestContext(request))


@login_required
def log_request(request):
    Room = roomexist('global')

    all_message = ChatMessage.objects.filter(destRoom=Room).filter(messType='normal')
    all_message = all_message[len(all_message)-50:] if len(all_message) > 50 else all_message

    return render_to_response('chat/global_log.html',
                            {
                            'log':all_message,
                            },
                            context_instance=RequestContext(request))


@login_required
def online_players(request):
    """ gather users online in the last ten minutes
    """
    oldest = datetime.now() - timedelta(minutes = 10)
    online_last10 = Player.objects.filter(last_seen__gte=oldest).order_by('user__username')

    def is_not_blocked(x):
        return not x.has_modifier('block-communication')

    online_last10 = filter(is_not_blocked, online_last10)

    return render_to_response('chat/chat_last.html',
                            {
                            'last': online_last10,
                            },
                            context_instance=RequestContext(request))



@login_required
def private_log(request):
    user = get_author(request)
    position = request.POST['number']
    room = roomexist(request.POST['room'])

    return HttpResponse(simplejson.dumps(some_old_message(user, room, position)))

@login_required
def archive_messages(request):

    room_name = request.POST['room']
    if room_name == 'global':
        date = request.POST['date']
        date = date.split("/", 4)
        hours = request.POST['hours']

        date_time_started = datetime(int(date[2]), int(date[0]), int(date[1]), int(date[3]), 0, 0)
        date_time_finished = datetime(int(date[2]), int(date[0]), int(date[1]), int(date[3]), 0, 0) + timedelta(hours = int(hours))
    else:
        date = request.POST['date']
        date = date.split("/", 3)

        date_time_started = datetime(int(date[2]), int(date[0]), int(date[1]), 0, 0, 0)
        date_time_finished = datetime(int(date[2]), int(date[0]), int(date[1]), 0, 0, 0) + timedelta(hours = 24)


    messages = ChatMessage.objects.filter(destRoom__name=room_name).filter(messType="normal").filter(timeStamp__gte=date_time_started).filter(timeStamp__lte=date_time_finished)


    user = get_author(request)
    obj = {'user': unicode(user)}
    obj['count'] = messages.count()
    msgs = []
    for i in messages:
        mesaj = {}
        mesaj['text'] = str(i)
        msgs.append(mesaj)

    obj['msgs'] = msgs
    return HttpResponse(simplejson.dumps(obj))


@login_required
def special_message(user, room = None, message = None):

    msgs = []
    mesaj = {
        'room':room,
        'user': user.nickname,
        'text': None,
        'mess_type': 'special',
        'comand': message,
        'dest_user':unicode(user.nickname)}
    msgs.append(mesaj)
    obj = {'user': unicode(user)}
    obj['count'] = 1
    obj['msgs'] = msgs
    return obj

@login_required
def sendmessage(request):
    """ Default endpoint (/chat/m/)
    """
    user = get_author(request)
    data = request.REQUEST

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
                        return json_response(serve_message(user))

                    if text[0] == '/kick':
                        add_message(text[1], user, room, sender, "special", "kick")
                    if text[0] == '/unban':
                        sender.canAccessChat = True
                        sender.save()
                    if text[0] == '/ban':
                        sender.canAccessChat = False
                        sender.save()
                    return json_response(serve_message(user))


        try:
            assert room is not None
            # content, author, room, user_to, messType, command
            add_message(data['msg'], user, room, user, "normal", "normal")
        except (ValueError, AssertionError):
            return HttpResponseBadRequest()
    elif data['opcode'] == 'keepAlive':
        chat_global = roomexist('global')
        if user.has_modifier('block-communication'):
            return json_response(special_message(user, None, "block-communication"))

            #add_message("", user, chat_global, user, "special", "block-communication")
        elif user.has_modifier('block-global-chat-page') or not user.canAccessChat:
            return json_response(special_message(user, None, "kick"))
            #add_message("", user, chat_global, user, "special", "kick")

        if user not in chat_global.participants.all():
            chat_global.participants.add(user)
    elif data['opcode'] == 'getRoom':
        try:
            user_to = Player.objects.get(id=data['to'])
            user_to = user_to.get_extension(ChatUser)
        except ChatUser.DoesNotExist:
            return HttpResponseBadRequest()
        if user.has_modifier('block-communication'):
            return HttpResponseBadRequest()
        if user_to.has_modifier('block-communication'):
            return HttpResponseBadRequest()
        rooms = ChatRoom.objects.exclude(name='global').filter(participants=user).filter(participants=user_to)
        rooms = [r for r in rooms if r.participants.count() <= 2]
        if len(rooms) > 1:
            return HttpResponseBadRequest()
        if rooms:
            room = rooms[0]
        else:
            name = '%d-%d' % ((user.id, user_to.id) if user.id < user_to.id else (user_to.id, user.id))
            room = ChatRoom.create(name)
        room.participants.add(user)
        room.participants.add(user_to.id)
        return json_response(room.to_dict())
    return json_response(serve_message(user))

def json_response(object):
     return HttpResponse(simplejson.dumps(object))

def roomexist(room_name):
    try:
        return ChatRoom.objects.get(name = room_name)
    except ChatRoom.DoesNotExist:
        return None

