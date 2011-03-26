from django.contrib.auth.models import User
from django.db.models import Q
from django.views.decorators.csrf import csrf_exempt
from wouso.interface import logger, render_response
from wouso.interface.forms import *

def homepage(request):
    """ First page shown """
    logger.debug('Everything is fine')

    return render_response('site_base.html', request)

@csrf_exempt
def search(request):
    logger.debug('Initiating search operation')
    form = SearchForm(request.POST)
    if form.is_valid():
        query = form.cleaned_data['query']
        searchresults = User.objects.filter(Q(first_name__icontains=query) | Q(last_name__icontains=query))
        print searchresults
        return render_response('search_results.html', request, {'searchresults': searchresults})

    return render_response('site_base.html', request)

