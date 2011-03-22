from django.contrib.auth.decorators import login_required
from django.http import Http404
from wouso.interface import render_response
from wouso.core.user.models import UserProfile

@login_required
def profile(request):
    return render_response('profile/index.html', request)  

@login_required
def user_profile(request, id):
    try:
        profile = UserProfile.objects.get(id=id)
    except UserProfile.DoesNotExist:
        raise Http404
        
    return render_response('profile/profile.html', 
        request,
        {'profile': profile})
