from django.contrib import admin
from interface.apps.lesson.models import Lesson, LessonCategory


admin.site.register(Lesson)
admin.site.register(LessonCategory)
