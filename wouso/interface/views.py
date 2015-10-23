import datetime
import logging
from django.conf import settings
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm
from django.core import serializers
from django.core.paginator import Paginator, InvalidPage, EmptyPage
from django.core.urlresolvers import reverse
from django.db.models import Q
from django.http import Http404, HttpResponseRedirect, HttpResponse
from django.shortcuts import render_to_response, get_object_or_404, redirect
from django.template import RequestContext
from django.views.decorators.csrf import csrf_exempt

from wouso.core import signals
from wouso.interface import logger, detect_mobile
from wouso.interface.apps.pages.models import NewsItem
from wouso.core.game import get_games
from wouso.interface.forms import *
from wouso.core.user.models import Race
from wouso.core.user.models import Player, PlayerGroup
from wouso.interface.activity.models import Activity
from wouso.interface.top.models import Top, TopUser, History as TopHistory


def get_wall(page=u'1'):
    """ Returns activity for main wall, paginated."""
    activity_list = Activity.get_global_activity()
    paginator = Paginator(activity_list, 10)
    try:
        activity = paginator.page(page)
    except (EmptyPage, InvalidPage):
        activity = paginator.page(paginator.num_pages)
    return activity

def anonymous_homepage(request):
    return render_to_response('splash.html', context_instance=RequestContext(request))


def login_view(request):
    # TODO: rethink and rewrite
    next = request.GET.get('next', '')
    if request.method != 'POST':
        form = AuthenticationForm(request)
        return render_to_response('registration/login.html', {'form': form, 'next': next},
            context_instance=RequestContext(request))
    else:
        form = AuthenticationForm(data=request.POST)
        if not form.is_valid():
            return render_to_response('registration/login.html', {'form': form, 'next': next},
                context_instance=RequestContext(request))

    user = authenticate(username=request.POST['username'], password=request.POST['password'])
    if user is not None:
        if user.is_active:
            #Save username in session
            PREFIX = "_user:"
            MAX_TIME = 48*60*60 #48h in seconds
            #Remove entries older than 48h
            for i in request.session.keys():
                if PREFIX in i and (request.session.get(i) + datetime.timedelta(minutes = 2*24*60)) < datetime.datetime.now():
                    request.session.__delitem__(i)
            request.session.__setitem__(PREFIX+user.username, datetime.datetime.now())
            request.session.set_expiry(MAX_TIME)
            login(request, user)
            signals.addActivity.send(sender=None, user_from=user.get_profile(), action="login", game = None, public=False)
            if request.POST.get('next'):
                return HttpResponseRedirect(request.POST.get('next'))
            return redirect(settings.LOGIN_REDIRECT_URL)
    return HttpResponseRedirect("/")


def logout_view(request):
    """
     This is used to save data in session after logout
    """
    data = {}
    PREFIX = "_user:"
    for i in request.session.keys():
        if PREFIX in i:
            data[i] = request.session.get(i)
    logout(request)
    for i in data:
        request.session[i] = data[i]
    return redirect('homepage')


def hub(request):
    if request.user.is_anonymous():
        return anonymous_homepage(request)

    # check first time
    profile = request.user.get_profile()
    activity = Activity.get_player_activity(profile).count()
    if activity < 2:
        # first timer, show povestea
        from wouso.interface.apps.pages.models import StaticPage
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
    topgroups = [profile.group] if profile.group else []
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
            if request.user.get_profile().in_staff_group():
                searchresults = Player.objects.filter(Q(user__first_name__icontains=query) | Q(user__last_name__icontains=query) |
                                                      Q(user__username__icontains=query) | Q(nickname__icontains=query)
                )
            else:
                searchresults = Player.objects.filter(Q(nickname__icontains=query))
            # special queries
            if query == 'outsiders':
                searchresults = Player.objects.filter(groups=None)
        else:
            query = query.split()
            searchresults = set()
            if request.user.get_profile().in_staff_group():
                for word in query:
                    r = Player.objects.filter(Q(user__first_name__icontains=word) | Q(user__last_name__icontains=word) |
                                          Q(nickname__icontains=query)
                    )
                    searchresults = searchresults.union(r)
            else:
                searchresults = Player.objects.filter(Q(nickname__icontains=query))

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
        if request.user.is_authenticated() and request.user.get_profile().in_staff_group():
            users = User.objects.filter(Q(first_name__icontains=query) |
                                        Q(last_name__icontains=query) |
                                        Q(username__icontains=query))
            user_ids = [u.id for u in users]
            searchresults = Player.objects.filter(Q(user__in=user_ids) |
                                                  Q(full_name__icontains=query) |
                                                  Q(nickname__icontains=query))
        else:
            searchresults = Player.objects.filter(Q(nickname__icontains=query))
        return render_to_response('interface/instant_search_results.txt',
                                  {'searchresults': searchresults},
                                  context_instance=RequestContext(request))

    else:
        return HttpResponse('')


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
    raise Http404


def ajax_get(request, model, id=0):
    if model == 'pages.staticpage':
        from wouso.interface.apps.pages.models import StaticPage
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
        for h in context.get('header', [])():
            count += h[0].get('count', 0)
    else:
        count = -1

    return HttpResponse('{"count": %d}' % count)


def no_api(request):
    return HttpResponse('API module inactive.')


def ui(request):
    """ Show the UI template. The rest is Javascript
    """

    return render_to_response('interface/ui.html', {}, context_instance=RequestContext(request))


def all_activity(request):
    """
     Render all public activity, no matter race or game
    """
    page = 1
    activity_list = Activity.get_global_activity(wouso_only=False)
    paginator = Paginator(activity_list, 100)
    try:
        activity = paginator.page(page)
    except (EmptyPage, InvalidPage):
        activity = paginator.page(paginator.num_pages)

    return render_to_response('activity/all.html', {'activity': activity}, context_instance=RequestContext(request))


@login_required
def seen_24h(request):
    """
    Display all players seen in the last 24h
    """
    oldest = datetime.datetime.now() - datetime.timedelta(minutes = 3600)
    online_last24h = Player.objects.filter(last_seen__gte=oldest).order_by('-last_seen')

    return render_to_response('activity/seen24h.html', {'seen_players': online_last24h}, context_instance=RequestContext(request))


@login_required()
def leaderboard_view(request):
    toptengroups = PlayerGroup.objects.exclude(parent=None).exclude(parent__can_play=False).order_by('-points')[:10]
    toptengroups = list(toptengroups)
    toptengroups.sort(key=lambda obj: obj.live_points, reverse=True)
    races = list(Race.objects.exclude(can_play=False))
    races.sort(key=lambda a: a.points, reverse=True)
    return render_to_response(('leaderboard.html'),
                              {'races':races, 'toptengroups':toptengroups, 'top':Top},
                              context_instance=RequestContext(request))


@login_required()
def division_view(request):
    profile = request.user.get_profile()

    division = profile.get_division(20)

    return render_to_response('division.html',
                              {'division': division},
                              context_instance=RequestContext(request))
