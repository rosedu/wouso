from wouso.games.challenge.models import Challenge, Question
from games.challenge.forms import challenge_form
from django.shortcuts import render_to_response
from django.http import HttpResponseRedirect
from django.template import RequestContext
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
import datetime

@login_required
def index(request):
    """ Shows all challenges related to the current user """
    challs = Challenge.get_active_challenges(request.user)
    
    played_challs = Challenge.get_played_challenges(request.user)[:10]
    
    return render_to_response('challenge/index.html', 
            {'challenges': challs, 'played': played_challs}, 
            context_instance=RequestContext(request))
    

@login_required    
def challenge(request, id):
    """ Plays challenge, only if status = accepted """
    try:
        chall = Challenge.objects.get(id=id)
    except Challenge.DoesNotExist:
        # TODO
        return HttpResponseRedirect("/challenge/?erororreu")
    
    # Check if this is a valid challenge
    if not chall.can_play(request.user):
        return HttpResponseRedirect("/challenge/?cantplay")
        
    if request.method == "POST":
        results = challenge_form(chall, request.POST)
        chall.set_played(request.user, results['points'])
        
        return render_to_response('challenge/result.html',
            {'challenge': chall, 'results': results},
            context_instance=RequestContext(request))
    else:
        forms = challenge_form(chall)
    return render_to_response('challenge/challenge.html',
            {'challenge': chall, 'forms': forms['forms']},
            context_instance=RequestContext(request))
    

@login_required
def launch(request, to_id):
    user_to = User.objects.get(id=to_id)
    
    user_from = request.user
    
    if user_from.get_profile().can_challenge(user_to.get_profile()):
        c = Challenge(user_from=user_from, user_to=user_to, 
            date=datetime.date.today())
        # insert in db
        c.save()
        # fetch questions
        if not c.create():
            """ Some error occurred. Clean up, and display error """
            c.delete()
            return HttpResponseRedirect("/challenge/?erorr_no_questions")
        # TODO: has_challenged
        
        return HttpResponseRedirect("/challenge/")
    else:
        # TODO: print info about the error
        return HttpResponseRedirect("/challenge/?erororr")

@login_required
def accept(request, id):
    try:
        chall = Challenge.objects.get(id=id)
    except Challenge.DoesNotExist:
        # TODO
        return HttpResponseRedirect("/challenge/?erororre")
    
    profile = request.user
    if chall.user_to == profile and chall.is_launched():
        chall.accept()
        return HttpResponseRedirect("/challenge/")
    return HttpResponseRedirect("/challenge/?erororrea")
    
@login_required
def refuse(request, id):
    try:
        chall = Challenge.objects.get(id=id)
    except Challenge.DoesNotExist:
        # TODO
        return HttpResponseRedirect("/challenge/?erororre")
    
    profile = request.user
    if chall.user_to == profile and chall.is_launched():
        chall.refuse()
        return HttpResponseRedirect("/challenge/")
    return HttpResponseRedirect("/challenge/?erororrea")
    
@login_required
def cancel(request, id):
    try:
        chall = Challenge.objects.get(id=id)
    except Challenge.DoesNotExist:
        # TODO
        return HttpResponseRedirect("/challenge/?erororre")
    
    profile = request.user
    if chall.user_from == profile and chall.is_launched():
        chall.cancel()
        return HttpResponseRedirect("/challenge/")
    return HttpResponseRedirect("/challenge/?erororrea")
