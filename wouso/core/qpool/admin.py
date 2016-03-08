from django.contrib import admin
from wouso.core.qpool import models
from django.forms import ModelForm


class AnswersInline(admin.TabularInline):
    model = models.Answer
    extra = 0
    verbose_name = "Answer"
    verbose_name_plural = "Answers"


class TagsInline(admin.TabularInline):
    model = models.Question.tags.through
    extra = 0
    verbose_name = "Tag"
    verbose_name_plural = "Tags"


class CategoryInline(admin.TabularInline):
    model = models.Question.category
    extra = 0
    verbose_name = "Category"
    verbose_name_plural = "Categories"


class ScheduleInline(admin.TabularInline):
    model = models.Schedule
    extra = 0
    verbose_name = "Day"


class QuestionForm(ModelForm):
    class Meta:
        model = models.Question

    def clean(self):
        # TODO: should check question type against number of
        # correct answers selected in AnswerInline
        return self.cleaned_data


class QuestionAdmin(admin.ModelAdmin):
    inlines = [AnswersInline, TagsInline, ScheduleInline]
    form = QuestionForm
    exclude = ('tags', )
    list_display = ('text', 'tags_nice', 'scheduled', 'category', 'active', 'id', 'proposed_by', 'endorsed_by')
    list_filter = ('active', 'category', 'tags')


class Questions2(admin.ModelAdmin):
    list_display = ('text')

admin.site.register(models.Question, QuestionAdmin)
admin.site.register(models.Tag)
admin.site.register(models.Category)
admin.site.register(models.Schedule)
