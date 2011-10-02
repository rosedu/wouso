from django.contrib import admin
from models import Artifact, Group, Spell

class SpellAdmin(admin.ModelAdmin):
    list_display = ('name', 'title', 'group', 'type', 'price')
admin.site.register(Artifact)
admin.site.register(Group)
admin.site.register(Spell, SpellAdmin)
