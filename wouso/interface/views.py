from django.contrib.auth.models import User
from django.db.models import Q
from django.views.decorators.csrf import csrf_exempt
from wouso.interface import logger, render_response
from wouso.interface.forms import *
from wouso.core.user.models import UserProfile
from wouso.interface.models import StaticPage

def homepage(request):
    """ First page shown """
    logger.debug('Everything is fine')

    return render_response('site_base.html', request)

@csrf_exempt
def search(request):
    """ Perform regular search by either first or last name """
    logger.debug('Initiating regular search')
    form = SearchForm(request.POST)
    if form.is_valid():
        query = form.cleaned_data['query']
        searchresults = User.objects.filter(Q(first_name__icontains=query) | Q(last_name__icontains=query))
        return render_response('search_results.html', request, {'searchresults': searchresults})

    return render_response('site_base.html', request)

def instantsearch(request):
    """ Perform instant search """
    logger.debug('Initiating instant search')
    form = InstantSearchForm(request.GET)
    if form.is_valid():
        query = form.cleaned_data['q']
        users = User.objects.filter(Q(first_name__icontains=query) | Q(last_name__icontains=query))
        user_ids = [u.id for u in users]
        searchresults = UserProfile.objects.filter(user__in=user_ids)
        return render_response('instant_search_results.txt', request, {'searchresults': searchresults})

@csrf_exempt
def staticpage(request, page_position):
    """ Perform regular search by either first or last name """
    logger.debug('Initiating regular search')
    staticpage = StaticPage.objects.get(position=int(page_position))
    return render_response('static_page.html', request, {'staticpage': staticpage})

