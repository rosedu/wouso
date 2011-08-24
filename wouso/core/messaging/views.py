from django.contrib.auth.decorators import login_required
from wouso.interface import render_response
from wouso.core.messaging.models import Message, MessageUser
from django.db.models import Q
from django.core.urlresolvers import reverse



@login_required
def inbox(request):
    
    profile = request.user.get_profile()
    msg_user = profile.get_extension(MessageUser)
    
    messages = Message.objects.filter(receiver=msg_user)
    
    return render_response('messaging/inbox.html',
                           request,
                           {'user': request.user,
                            'messages': messages})


@login_required
def sentbox(request):
    
    profile = request.user.get_profile()
    msg_user = profile.get_extension(MessageUser)
    
    messages = Message.objects.filter(sender=msg_user)
    
    return render_response('messaging/sentbox.html',
                           request,
                           {'user': request.user,
                            'messages': messages})


@login_required
def allbox(request):
    
    profile = request.user.get_profile()
    msg_user = profile.get_extension(MessageUser)
    
    messages = Message.objects.filter(Q(receiver=msg_user) | Q(sender=msg_user))
    
    return render_response('messaging/allbox.html',
                           request,
                           {'user': request.user,
                            'messages': messages})



@login_required
def create(request):
    
    return render_response('messaging/create.html', request)
    

def header_link(request):
    return '<a href="'+ reverse('wouso.core.messaging.views.inbox') +'">Messages</a>'