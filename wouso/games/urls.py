import os
import os.path
from django.conf.urls.defaults import *
from django.conf import settings

upat = [(r'^$', 'views.games'),]

games_dir = os.path.abspath(os.path.dirname(__file__))

for g in os.listdir(games_dir):
    if os.path.exists(games_dir + '/' + g + '/urls.py'):
        upat.append((r'{game}'.format(game=g), include('games.{game}.urls'.format(game=g))))

urlpatterns = patterns('games', *upat)

