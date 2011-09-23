from django.contrib import admin
from django.contrib.auth.models import User
from django.contrib.auth.admin import UserAdmin as OldUserAdmin
from wouso.core.user.models import (Player, PlayerGroup,
                                    PlayerArtifactAmount,
                                    PlayerSpellAmount,
                                    PlayerSpellDue)

class UserProfileInline(admin.StackedInline):
    model = Player

class UserAdmin(OldUserAdmin):
    inlines = [ UserProfileInline ]

admin.site.unregister(User)
admin.site.register(User, UserAdmin)

admin.site.register(PlayerGroup)
admin.site.register(PlayerArtifactAmount)
admin.site.register(PlayerSpellAmount)
admin.site.register(PlayerSpellDue)
