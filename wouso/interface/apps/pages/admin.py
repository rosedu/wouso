from django.contrib import admin
from wouso.interface.apps.pages.models import StaticPage, NewsItem

admin.site.register(StaticPage)
admin.site.register(NewsItem)
