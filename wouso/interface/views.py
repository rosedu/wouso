import datetime
from django.contrib.auth.models import User
from django.core.paginator import Paginator, InvalidPage, EmptyPage
from django.db.models import Q
from django.views.decorators.csrf import csrf_exempt
from django.http import Http404
from django.shortcuts import render_to_response
from django.template import RequestContext
from wouso.interface import logger
from django.utils.translation import ugettext as _
from wouso.interface.forms import *
from wouso.core.user.models import Player
from wouso.interface.models import StaticPage
from wouso.interface.activity.models import Activity


def get_wall(page=u'1'):
    ''' Returns activity for main wall, paginated.'''
    activity_list = Activity.objects.all().order_by('-timestamp')
    paginator = Paginator(activity_list, 10)
    try:
        activity = paginator.page(page)
    except (EmptyPage, InvalidPage):
        activity = paginator.page(paginator.num_pages)
    return activity

def homepage(request, page=u'1'):
    """ First page shown """
    # gather users online in the last ten minutes
    oldest = datetime.datetime.now() - datetime.timedelta(minutes = 10)
    online_last10 = Player.objects.filter(last_seen__gte=oldest)
    activity = get_wall(page)

    return render_to_response('site_base.html',
                              {'last10': online_last10, 'activity': activity},
                              context_instance=RequestContext(request))

@csrf_exempt
def search(request):
    """ Perform regular search by either first or last name """
    logger.debug('Initiating regular search')
    form = SearchForm(request.POST)
    if form.is_valid():
        query = form.cleaned_data['query']
        if len(query.split()) == 1:
            searchresults = Player.objects.filter(Q(user__first_name__icontains=query) | Q(user__last_name__icontains=query))
        else:
            query = query.split()
            searchresults = set()
            for word in query:
                r = Player.objects.filter(Q(user__first_name__icontains=word) | Q(user__last_name__icontains=word))
                searchresults = searchresults.union(r)

        return render_to_response('search_results.html',
                                  {'searchresults': searchresults},
                                  context_instance=RequestContext(request))

    return render_to_response('site_base.html', context_instance=RequestContext(request))

def instantsearch(request):
    """ Perform instant search """
    logger.debug('Initiating instant search')
    form = InstantSearchForm(request.GET)
    if form.is_valid():
        query = form.cleaned_data['q']
        users = User.objects.filter(Q(first_name__icontains=query) | Q(last_name__icontains=query))
        user_ids = [u.id for u in users]
        searchresults = Player.objects.filter(user__in=user_ids)
        return render_to_response('instant_search_results.txt',
                                  {'searchresults': searchresults},
                                  context_instance=RequestContext(request))


def searchone(request):
    """ Get one user, based on his/her name """
    logger.debug('Initiating search one')
    form = SearchOneForm(request.GET)
    if form.is_valid():
        query = form.cleaned_data['q']
        result = []
        try:
            first = query.split(' ')[0]
            users = User.objects.filter(Q(first_name__icontains=first))
            for u in users:
                name = u.first_name + " " + u.last_name
                if name == query:
                    result.append(u)
            if result:
                return render_to_response('search_one_results.txt',
                                          {'results': result},
                                          context_instance=RequestContext(request))
        except Exception as e:
            logging.exception(e)

    raise Http404()

@csrf_exempt
def staticpage(request, slug):
    """ Perform regular search by either first or last name """
    logger.debug('Initiating regular search')
    staticpage = StaticPage.objects.get(slug=slug)
    return render_to_response('static_page.html',
                              {'staticpage': staticpage},
                              context_instance=RequestContext(request))
