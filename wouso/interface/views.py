import datetime
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator, InvalidPage, EmptyPage
from django.core import serializers
from django.core.urlresolvers import reverse
from django.db.models import Q
from django.views.decorators.csrf import csrf_exempt
from django.http import Http404, HttpResponseRedirect, HttpResponse
from django.shortcuts import render_to_response, get_object_or_404
from django.template import RequestContext
from django.utils.translation import ugettext as _
from wouso.interface import logger, detect_mobile
from wouso.interface.pages.models import NewsItem
from wouso.core.game import get_games
from wouso.interface.forms import *
from wouso.core.user.models import Player, PlayerGroup
from wouso.core.magic.models import Spell
from wouso.core import scoring
from wouso.interface.activity.models import Activity
from wouso.interface.top.models import TopUser, History as TopHistory

def get_wall(page=u'1'):
    ''' Returns activity for main wall, paginated.'''
    activity_list = Activity.objects.all().exclude(user_from__groups__name='Others', game__isnull=False).order_by('-timestamp')
    paginator = Paginator(activity_list, 10)
    try:
        activity = paginator.page(page)
    except (EmptyPage, InvalidPage):
        activity = paginator.page(paginator.num_pages)
    return activity

def anonymous_homepage(request):
    return render_to_response('splash.html', context_instance=RequestContext(request))

def hub(request):
    if request.user.is_anonymous():
        return anonymous_homepage(request)

    # check first time
    profile = request.user.get_profile()
    activity = Activity.objects.filter(user_from=profile).count()
    if activity < 2:
        # first timer, show povestea
        from wouso.interface.pages.models import StaticPage
        try:
            story = StaticPage.objects.get(slug='poveste')
        except: pass
        else:
            return HttpResponseRedirect(reverse('static_page', args=(story.slug,)))
    return homepage(request)

def homepage(request, page=u'1'):
    """ First page shown """
    if request.user.is_anonymous():
        return anonymous_homepage(request)

    profile = request.user.get_profile()
    # gather users online in the last ten minutes
    oldest = datetime.datetime.now() - datetime.timedelta(minutes = 10)
    online_last10 = Player.objects.filter(last_seen__gte=oldest).order_by('-last_seen')
    activity = get_wall(page)

    topuser = profile.get_extension(TopUser)
    topgroups = list(profile.groups.all())
    for g in topgroups:
        g.position = TopHistory.get_user_position(topuser, relative_to=g)

    if detect_mobile(request):
        template = 'mobile_index.html'
    else:
        template = 'site_index.html'

    news = NewsItem.objects.all().order_by('-date_pub', '-id')
    more = False
    if len(news) > 10:
        more = True
    news = news[:10]

    return render_to_response(template,
                              {'last10': online_last10, 'activity': activity,
                              'is_homepage': True,
                              'top': topuser,
                              'topgroups': topgroups,
                              'games': get_games(),
                              'news': news,
                              'more': more,
                              },
                              context_instance=RequestContext(request))

@csrf_exempt
def search(request):
    """ Perform regular search by either first or last name """
    logger.debug('Initiating regular search')
    form = SearchForm(request.POST)
    if form.is_valid():
        query = form.cleaned_data['query']
        if len(query.split()) == 1:
            searchresults = Player.objects.filter(Q(user__first_name__icontains=query) | Q(user__last_name__icontains=query) | Q(user__username__icontains=query))
            # special queries
            if query == 'outsiders':
                searchresults = Player.objects.filter(groups=None)
        else:
            query = query.split()
            searchresults = set()
            for word in query:
                r = Player.objects.filter(Q(user__first_name__icontains=word) | Q(user__last_name__icontains=word))
                searchresults = searchresults.union(r)

        # search groups
        group_results = PlayerGroup.objects.filter(Q(name__icontains=query)|Q(title__icontains=query))

        return render_to_response('interface/search_results.html',
                                  {'searchresults': searchresults,
                                   'groupresults': group_results,
                                   'search_query': form.cleaned_data['query']},
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

        return render_to_response('interface/instant_search_results.txt',
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
                return render_to_response('interface/search_one_results.txt',
                                          {'results': result},
                                          context_instance=RequestContext(request))
        except Exception as e:
            logging.exception(e)

    raise Http404()

def ajax(request, name):
    if name == 'header':
        return render_to_response('interface/header.html',
                                context_instance=RequestContext(request))
    if name == 'activity':
        return render_to_response('activity/stream.html',
                                {'activity': get_wall(),},
                                context_instance=RequestContext(request))
    raise Http404

def ajax_get(request, model, id=0):
    if model == 'pages.staticpage':
        from wouso.interface.pages.models import StaticPage
        model = StaticPage
    else:
        raise Http404

    obj = get_object_or_404(model, pk=id)

    return HttpResponse(serializers.serialize('json', (obj,)))

def ajax_notifications(request):
    if request.user.is_authenticated():
        context = RequestContext(request)
        count = 0
        # TODO use reduce
        for h in context.get('heads', []):
            count += h[0].get('count', 0)
    else:
        count = -1

    return HttpResponse('{"count": %d}' % count)
