from django.contrib import admin
from models import Artifact, ArtifactGroup, Spell

class SpellAdmin(admin.ModelAdmin):
    list_display = ('name', 'title', 'group', 'type', 'price')
admin.site.register(Artifact)
admin.site.register(ArtifactGroup)
admin.site.register(Spell, SpellAdmin)
