from django.contrib.auth.decorators import login_required
from wouso.interface import render_response

@login_required
def profile(request):
    return render_response('profile/index.html', request)  
