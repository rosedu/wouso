from django.contrib import admin
from django.contrib.auth.models import User
from django.contrib.auth.admin import UserAdmin as OldUserAdmin
from wouso.games.challenge.models import *

admin.site.register(Challenge)

class AnswerInline(admin.TabularInline):
    model = Answer
    extra = 4
    max_num = 4
    min_num = 4

class QuestionAdmin(admin.ModelAdmin):
    inlines = [AnswerInline]
    
admin.site.register(Question, QuestionAdmin)
