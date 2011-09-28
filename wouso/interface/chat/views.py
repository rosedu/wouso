from django.core.urlresolvers import reverse
from django.http import HttpResponse, HttpResponseRedirect, HttpResponseBadRequest
from django.contrib.auth.decorators import login_required
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.utils import simplejson
from models import *
from datetime import datetime, timedelta

def create_room(roomName, deletable=False, renameable=False):
    ''' creates a new chatroom and saves it '''
    newRoom = ChatRoom(name=roomName, deletable=deletable, renameable=renameable)
    newRoom.save()

def get_author(request):

    return request.user.get_profile().get_extension(ChatUser)

def add_message(text, sender, toRoom):

    timeStamp = datetime.now()

    diff = timeStamp - sender.lastMessageTS

    if diff.total_seconds() > 0.5:
        msg = ChatMessage(content=text, author=sender, destRoom=toRoom, timeStamp=timeStamp)
        msg.save()
    else:
        raise ValueError('Spam')

def serve_message(user):

    obj = {'user': unicode(user)}
    query = ChatMessage.objects.filter(timeStamp__gt=user.lastMessageTS)
    obj['count'] = query.count()

    if not query:
        return None

    msgs = []
    for m in query:
        mesaj = {}
        mesaj['room'] = ''
        mesaj['user'] = unicode(m.author)
        mesaj['text'] = m.content
        lastTS = m.timeStamp
        msgs.append(mesaj)
    user.lastMessageTS = lastTS
    user.save()

    obj['msgs'] = msgs

    return obj

@login_required
def index(request):
    user = request.user.get_profile()
    return render_to_response('chat.html', {'user': user},
            context_instance=RequestContext(request))

@login_required
def sendmessage(request):
    user = get_author(request)
    if request.POST['opcode'] == 'message':
        try:
            add_message(request.POST['msg'], user, None)
        except ValueError:
            return HttpResponseBadRequest()
    
    return HttpResponse(simplejson.dumps(serve_message(user)))
