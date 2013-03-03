from django.contrib import admin
from wouso.games.challenge.models import Challenge, ChallengeUser, Participant

class ChallengeUserAdmin(admin.ModelAdmin):
    list_display = ('__unicode__', 'last_launched')

admin.site.register(Challenge)
admin.site.register(Participant)
admin.site.register(ChallengeUser, ChallengeUserAdmin)
