from models import Question, WQuest
from django.contrib import admin

class QuestionInline(admin.TabularInline):
    model = Question
    min_num = 5

class QuestAdmin(admin.ModelAdmin):
    inlines = [QuestionInline]

admin.site.register(WQuest, QuestAdmin)
