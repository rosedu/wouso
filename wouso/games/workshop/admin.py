from django.contrib import admin
from models import Schedule, Semigroup, Assessment, Workshop, Review, Answer

admin.site.register(Schedule)
admin.site.register(Semigroup)
admin.site.register(Assessment)
admin.site.register(Workshop)

class RAdmin(admin.ModelAdmin):
    list_filter = ('answer__assessment', 'answer__assessment__workshop', 'answer', 'reviewer')
    list_display = ('id', 'workshop', 'reviewer', 'feedback', 'answer_grade', 'review_grade')

admin.site.register(Review, RAdmin)
admin.site.register(Answer)