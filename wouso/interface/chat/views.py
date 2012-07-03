from django.core.urlresolvers import reverse
from django.http import HttpResponse, HttpResponseRedirect, HttpResponseBadRequest
from django.contrib.auth.decorators import login_required
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.utils import simplejson
from models import *
from forms import *


from wouso.core.config.models import BoolSetting
from datetime import datetime, timedelta
#import datetime


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
    if BoolSetting.get('disable-Chat').get_value():
        return HttpResponseRedirect(reverse('wouso.interface.views.homepage'))

    user = request.user.get_profile()
    return render_to_response('chat.html', 
							{'user': user,
							},
           					context_instance=RequestContext(request))

@login_required
def log_request(request):

    all_message = ChatMessage.objects.all()
    all_message = all_message[len(all_message)-50:] if len(all_message) > 50 else all_message

    return render_to_response('online.html', 
							{
							'log':all_message,
							},
           					context_instance=RequestContext(request))
    
@login_required
def online_players(request):

    # gather users online in the last ten minutes
    oldest = datetime.now() - timedelta(minutes = 10)
    online_last10 = Player.objects.filter(last_seen__gte=oldest).order_by('-last_seen')

    return render_to_response('chat_last.html',
							{
							'last': online_last10,
							},
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


def header_link(request):


    url = reverse('wouso.interface.chat.views.index')
    return dict(link=url, count=10, text=_('Meages'))