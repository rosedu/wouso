from django.contrib import admin
from wouso.games.challenge.models import Challenge, ChallengeUser, Participant

admin.site.register(Challenge)
admin.site.register(Participant)
admin.site.register(ChallengeUser)
