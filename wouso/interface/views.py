import datetime
from django.contrib.auth.models import User
from django.core.paginator import Paginator, InvalidPage, EmptyPage
from django.db.models import Q
from django.views.decorators.csrf import csrf_exempt
from django.http import Http404, HttpResponseRedirect
from django.shortcuts import render_to_response, get_object_or_404
from django.template import RequestContext
from wouso.interface import logger
from django.utils.translation import ugettext as _
from wouso.interface.forms import *
from wouso.core.user.models import Player
from wouso.core.magic.models import Spell
from wouso.core import scoring
from wouso.interface.activity.models import Activity
from wouso.interface.top.models import TopUser, History as TopHistory

def get_wall(page=u'1'):
    ''' Returns activity for main wall, paginated.'''
    activity_list = Activity.objects.all().order_by('-timestamp')
    paginator = Paginator(activity_list, 10)
    try:
        activity = paginator.page(page)
    except (EmptyPage, InvalidPage):
        activity = paginator.page(paginator.num_pages)
    return activity

def anonymous_homepage(request):
    return render_to_response('splash.html', context_instance=RequestContext(request))

def homepage(request, page=u'1'):
    """ First page shown """
    if request.user.is_anonymous():
        return anonymous_homepage(request)

    profile = request.user.get_profile()
    # gather users online in the last ten minutes
    oldest = datetime.datetime.now() - datetime.timedelta(minutes = 10)
    online_last10 = Player.objects.filter(last_seen__gte=oldest)
    activity = get_wall(page)

    topuser = profile.get_extension(TopUser)
    topgroups = list(profile.groups.all().order_by('-gclass'))
    for g in topgroups:
        g.position = TopHistory.get_user_position(topuser, relative_to=g)

    return render_to_response('site_base.html',
                              {'last10': online_last10, 'activity': activity,
                              'is_homepage': True,
                              'top': topuser,
                              'topgroups': topgroups,
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

# marche

def market(request):
    spells = Spell.objects.all()

    return render_to_response('market.html', {'spells': spells},
                              context_instance=RequestContext(request))

def market_buy(request, spell):
    spell = get_object_or_404(Spell, pk=spell)

    player = request.user.get_profile()
    error, message = '',''
    if spell.price > player.coins.get('gold', 0):
        error = _("Insufficient gold amount")
    else:
        player.add_spell(spell)
        scoring.score(player, None, 'buy-spell', external_id=spell.id,
                      price=spell.price)
        message = _("Successfully aquired")

    return render_to_response('market_buy.html', {'error': error, 'message': message},
                              context_instance=RequestContext(request))
