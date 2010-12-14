from django.shortcuts import render_to_response
from django.template import RequestContext
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from core.profile.models import UserProfile, Message
from core.profile.forms import MessageForm
import datetime

@login_required
def index(request):
    return render_to_response('user/profile.html', {'profile': request.user.get_profile()}, context_instance=RequestContext(request))
    
def user_profile(request, id):
    """ Shows user's specified by id profile """
    profile = UserProfile.objects.get(user=User.objects.get(id=id))
    try:
        can_challenge = request.user.get_profile().can_challenge(profile)
    except AttributeError:
        can_challenge = False
    
    return render_to_response('user/profile.html', 
            {'profile': profile, 'can_challenge': can_challenge}, 
            context_instance=RequestContext(request))

def top(request):
    """ Shows all users 
    TODO: pagination, sorting """
    players = UserProfile.objects.all()
    
    return render_to_response('user/top.html', {'users': players},
            context_instance=RequestContext(request))
            
def search(request):
    """ Search for an user """
    query = request.GET.get('query', None)
    # TODO: sanitize query!
    
    if query == None:
        players = None
    else:
        players = UserProfile.objects.filter(real_name__contains=query)
    
    return render_to_response('user/search.html', 
            {'users': players, 'query': query},
            context_instance=RequestContext(request))

@login_required
def messages(request):
    """ Show all messages """
    profile = request.user.get_profile()
    msgs = profile.get_all_messages()
    
    return render_to_response('user/messages.html', 
            {'messages': msgs},
            context_instance=RequestContext(request))

@login_required
def message(request, idmsg):
    """ Display specific message """
    try:
        msg = Message.objects.get(id=idmsg)
        if msg.user_from != request.user and msg.user_to != request.user:
            raise Message.DoesNotExist()
    except Message.DoesNotExist:
        return HttpResponseRedirect(reverse('wouso.core.profile.views.messages'))
    
    if msg.user_to == request.user:
        msg.read = True
        msg.save()
    
    return render_to_response('user/message.html', 
            {'message': msg},
            context_instance=RequestContext(request))

@login_required
def message_compose(request, idto):
    try:
        user_to = User.objects.get(id=idto)
    except User.DoesNotExist:
        # TODO: display an error
        return HttpResponseRedirect(reverse('wouso.core.profile.views.messages'))
    
    if request.method == "POST":
        form = MessageForm(request.POST)
        new_message = form.save(commit=False)
        new_message.user_from = request.user
        new_message.user_to = user_to
        new_message.date = datetime.datetime.now()
        new_message.save()
        return HttpResponseRedirect(reverse('wouso.core.profile.views.messages')) #TODO message sent
    else:
        form = MessageForm()
        
    return render_to_response('user/message_compose.html', 
            {'user_to': user_to, 'form': form},
            context_instance=RequestContext(request))
