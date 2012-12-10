from django.contrib import admin
from wouso.games.grandchallenge.models import GrandChallenge, GrandChallengeUser, GrandChallengeGame

admin.site.register(GrandChallenge)
admin.site.register(GrandChallengeGame)
admin.site.register(GrandChallengeUser)