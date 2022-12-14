from django.contrib import admin
from models import Activity


class ActivityAdmin(admin.ModelAdmin):
    list_display = ('timestamp', 'user_from', 'user_to', 'game_name', 'message')
    list_filter = ('game', )


admin.site.register(Activity, ActivityAdmin)
