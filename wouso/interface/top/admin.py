from django.contrib import admin
from wouso.interface.top.models import TopUser, History, NewHistory

admin.site.register(TopUser)
admin.site.register(History)


class NHAdmin(admin.ModelAdmin):
    list_display = ('date', 'object', 'object_type', 'relative_to', 'relative_to_type', 'position')


admin.site.register(NewHistory, NHAdmin)
