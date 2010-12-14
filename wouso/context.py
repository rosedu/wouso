# Context Processor for the template engine
from wouso.games.qotd.models import Question
from wouso.games.wquest.models import WQuest
from wouso.core.profile.models import UserProfile
import datetime
import gamesettings as info

def config(request):
    """ Return configuration specific data """
    theme = request.GET.get('theme', info.DEFAULT_THEME)
    elapsed = datetime.datetime.today() - info.START_DATE
    remaining = info.END_DATE - datetime.datetime.today()
    if datetime.datetime.today() < info.START_DATE:
        elapsed = 0
        started = False
    else:
        started = True
    # Get current game-week
    week = elapsed.days % 7
    return {'config':   {'theme': theme },
            'game':     {'start': info.START_DATE, 'end': info.END_DATE, 
                        'elapsed': elapsed, 'remaining': remaining, 
                        'started': started, 'title': info.GAME_TITLE,
                        'week': week,
                        'chapter': info.CURRENT_CHAPTER}
            }
    
def games_info(request):
    current = Question.get_for_today()
    
    if current == None:
        qotd = {'valid': False}
    else:
        qotd = {'valid': True, 'text': current.text}
        
    return {
        'qotd': qotd,
        'challegens_info': None,
        'quest': WQuest.get_current()
        }
    
def userprofile(request):
    try:
        profile = request.user.get_profile()
        # Update last_online here.
        profile.last_online = datetime.datetime.now()
        profile.save()
    except:
        profile = None
        
    return {'userprofile': profile}
    
def top10(request):
    #try:
    users = UserProfile.objects.all().order_by('-points')[:10]
    #except:
    #    users = None
        
    return {'top10': users}

