from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.shortcuts import get_object_or_404
from django.http import HttpResponseRedirect, Http404
from django.core.urlresolvers import reverse
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.utils.translation import ugettext as _
from wouso.core.user.models import Player
from wouso.interface.apps.messaging.models import Message, MessagingUser, MessageApp
from wouso.interface.apps.messaging.forms import ComposeForm


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
    else:
        messages = Message.objects.none()

    messages = messages.order_by('-timestamp')[:100] # Temporary fix until we introduce archive and trash (do not actually delete for auditing)

    if quiet is not None:
        template = 'messaging/message.html'
    else:
        template = 'messaging/index.html'

    return render_to_response(template,
                              {'user': request.user,
                               'messages_list': messages,
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

    error = ''
    if request.method == "POST":
        form = ComposeForm(request.POST)
        if form.is_valid():
            m = Message.send(request.user.get_profile(),
                            form.cleaned_data['to'],
                            form.cleaned_data['subject'],
                            form.cleaned_data['text'],
                            reply_to=form.cleaned_data['reply_to'],
            )
            if m is None:
                return HttpResponseRedirect(reverse('messaging'))
            else:
                error = m
        #else:
        #   print form, form.is_valid(), request.POST
    return render_to_response('messaging/create.html',
                              {'error': error, 'to': to,
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

@login_required
def delete(request, id):
    message = get_object_or_404(Message, pk=id)
    message.delete()
    go_back = request.META.get('HTTP_REFERER', None)
    if not go_back:
        go_back = reverse('wouso.interface.messaging.views.home')
    return HttpResponseRedirect(go_back)


def header_link(request):
    # TODO refactor this lame thing
    count = MessageApp.get_unread_count(request)
    url = reverse('messaging')
    return dict(link=url, count=count, text=_('Messages'))
