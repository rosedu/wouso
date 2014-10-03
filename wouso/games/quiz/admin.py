from django.contrib import admin

from models import QuizUser, Quiz, QuizGame

admin.site.register(Quiz)
admin.site.register(QuizGame)
admin.site.register(QuizUser)
