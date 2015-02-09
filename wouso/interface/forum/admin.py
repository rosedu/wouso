from django.contrib import admin
from wouso.interface.forum.models import Category, Forum, Topic, Post


admin.site.register(Category)
admin.site.register(Forum)
admin.site.register(Topic)
admin.site.register(Post)
