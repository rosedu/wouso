from django.contrib import admin
from wouso.games.challenge.models import Challenge, ChallengeUser

admin.site.register(Challenge)
admin.site.register(ChallengeUser)
