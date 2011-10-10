from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.shortcuts import get_object_or_404
from django.http import HttpResponseRedirect, Http404
from django.core.urlresolvers import reverse
from django.core.paginator import Paginator, InvalidPage, EmptyPage
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.utils.translation import ugettext as _
from wouso.core.user.models import Player
from wouso.interface.messaging.models import Message, MessagingUser
from wouso.interface.messaging.forms import ComposeForm


@login_required
def home(request, quiet=None, box=None, page=u'0'):

    profile = request.user.get_profile()
    msg_user = profile.get_extension(MessagingUser)

    if box == 'rec' or box is None:
        messages = Message.objects.filter(receiver=msg_user)
    elif box == 'sent':
        messages = Message.objects.filter(sender=msg_user)
    elif box == 'all':
        messages = Message.objects.filter(Q(receiver=msg_user) | Q(sender=msg_user))

    messages = messages.order_by('-timestamp')

    if quiet is not None:
        template = 'messaging/message.html'
    else:
        template = 'messaging/index.html'

    return render_to_response(template,
                              {'user': request.user,
                               'messages': messages,
                               'box': box,
                               },
                              context_instance=RequestContext(request))


@login_required
def create(request, to=None, reply_to=None):
    if to is not None:
        to = get_object_or_404(Player, pk=to)
    if reply_to is not None:
        reply_to = get_object_or_404(Message, pk=reply_to)
        subject = 'Re: ' + reply_to.subject if not reply_to.subject.startswith('Re: ') else reply_to.subject
    else:
        subject = ''

    if request.method == "POST":
        form = ComposeForm(request.POST)
        if form.is_valid():
            m = Message.send(request.user.get_profile(),
                            form.cleaned_data['to'],
                            form.cleaned_data['subject'],
                            form.cleaned_data['text'],
                            reply_to=form.cleaned_data['reply_to'],
            )
            return HttpResponseRedirect(reverse('wouso.interface.messaging.views.home'))
        #else:
        #   print form, form.is_valid(), request.POST
    return render_to_response('messaging/create.html',
                              {'to': to,
                               'reply_to': reply_to,
                               'subject': subject},
                              context_instance=RequestContext(request))

@login_required
def message(request, mid):
    message = get_object_or_404(Message, pk=mid)

    me = request.user.get_profile().get_extension(MessagingUser)

    if message.sender == me or message.receiver == me:
        if message.receiver == me:
            message.read = True
            message.save()
        return render_to_response('messaging/message_one.html',
                                  {'m': message, 'mess_user': me},
                                  context_instance=RequestContext(request))
    raise Http404

def header_link(request):
    profile = request.user.get_profile()
    if not profile:
        return ''

    msg_user = profile.get_extension(MessagingUser)
    msgs = Message.objects.filter(receiver=msg_user).filter(read=False)
    count = len(msgs)

    link = '<a href="'+ reverse('wouso.interface.messaging.views.home') +'">' + _('Messages') + '</a>'
    if count > 0:
        link += '<span class="unread-count">%d</span>' % count
    return link
