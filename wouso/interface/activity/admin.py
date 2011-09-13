from django.contrib import admin
from models import Activity

class ActivityAdmin(admin.ModelAdmin):
    list_display = ('timestamp', 'user_from', 'user_to', 'game_name', 'message')

admin.site.register(Activity, ActivityAdmin)
