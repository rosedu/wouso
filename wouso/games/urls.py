import os
import os.path
from django.conf.urls.defaults import *
from wouso.games import get_games

from django.conf import settings

upat = [url(r'^$', 'views.games', name='games'),]

for g in get_games():
    upat.append((r'^{game}/'.format(game=g), include('games.{game}.urls'.format(game=g))))

urlpatterns = patterns('games', *upat)

