from wouso.games.qotd.models import Question, Answer
from django.contrib import admin

class AnswerInline(admin.TabularInline):
    model = Answer
    extra = 4
    max_num = 4
    min_num = 4

class QuestionAdmin(admin.ModelAdmin):
    inlines = [AnswerInline]

admin.site.register(Question, QuestionAdmin)
