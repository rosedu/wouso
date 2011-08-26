from django.contrib.auth.decorators import login_required
from wouso.interface import render_response
from wouso.interface.messaging.models import Message, MessagingUser
from django.db.models import Q
from django.core.urlresolvers import reverse



@login_required
def home(request):

    profile = request.user.get_profile()
    msg_user = profile.get_extension(MessagingUser)

    messages_rec = Message.objects.filter(receiver=msg_user)
    messages_sent = Message.objects.filter(receiver=msg_user)
    messages_all = Message.objects.filter(Q(receiver=msg_user) | Q(sender=msg_user))

    return render_response('messaging/inbox.html',
                           request,
                           {'user': request.user,
                            'messages_rec': messages_rec,
                            'messages_sent': messages_sent,
                            'messages_all': messages_all
                            })


@login_required
def create(request):

    return render_response('messaging/create.html', request)


def header_link(request):
    return '<a href="'+ reverse('wouso.interface.messaging.views.inbox') +'">Messages</a>'
