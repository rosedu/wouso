from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.shortcuts import get_object_or_404
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse
from wouso.core.user.models import UserProfile
from wouso.interface import render_response
from wouso.interface.messaging.models import Message, MessagingUser
from wouso.interface.messaging.forms import ComposeForm

@login_required
def inbox(request):

    profile = request.user.get_profile()
    msg_user = profile.get_extension(MessagingUser)

    messages = Message.objects.filter(receiver=msg_user)

    return render_response('messaging/inbox.html',
                           request,
                           {'user': request.user,
                            'messages': messages})


@login_required
def sentbox(request):

    profile = request.user.get_profile()
    msg_user = profile.get_extension(MessagingUser)

    messages = Message.objects.filter(sender=msg_user)

    return render_response('messaging/sentbox.html',
                           request,
                           {'user': request.user,
                            'messages': messages})


@login_required
def allbox(request):

    profile = request.user.get_profile()
    msg_user = profile.get_extension(MessagingUser)

    messages = Message.objects.filter(Q(receiver=msg_user) | Q(sender=msg_user))

    return render_response('messaging/allbox.html',
                           request,
                           {'user': request.user,
                            'messages': messages})



@login_required
def create(request, to=None):
    if to is not None:
        to = get_object_or_404(UserProfile, pk=to)

    if request.method == "POST":
        form = ComposeForm(request.POST)
        if form.is_valid():
            m = Message.send(request.user.get_profile(),
                            form.cleaned_data['to'],
                            form.cleaned_data['subject'],
                            form.cleaned_data['text']
            )
            return HttpResponseRedirect(reverse('wouso.interface.messaging.views.inbox'))
        #else:
        #   print form, form.is_valid(), request.POST
    return render_response('messaging/create.html', request, {'to': to})


def header_link(request):
    return '<a href="'+ reverse('wouso.interface.messaging.views.inbox') +'">Messages</a>'
