from django.contrib.auth.decorators import login_required
from wouso.interface import render_response
from wouso.interface.messaging.models import Message, MessagingUser
from django.db.models import Q
from django.core.urlresolvers import reverse
from django.core.paginator import Paginator, InvalidPage, EmptyPage




@login_required
def home(request, quiet=None, box=None, page=u'0'):

    profile = request.user.get_profile()
    msg_user = profile.get_extension(MessagingUser)

    if box == 'rec' or box is None:
        messages = Message.objects.filter(receiver=msg_user)
    elif box == 'sent':
        messages = Message.objects.filter(receiver=msg_user)
    elif box == 'all':
        messages = Message.objects.filter(Q(receiver=msg_user) | Q(sender=msg_user))

    if quiet is not None:
        template = 'messaging/message.html'
    else:
        template = 'messaging/index.html'

    return render_response(template,
                           request,
                           {'user': request.user,
                            'messages': messages
                            })


@login_required
def create(request):

    return render_response('messaging/create.html', request)


def header_link(request):
    return '<a href="'+ reverse('wouso.interface.messaging.views.home') +'">Messages</a>'
