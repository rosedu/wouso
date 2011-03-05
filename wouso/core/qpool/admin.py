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
    
class QuestionForm(ModelForm):
    class Meta:
        model = models.Question
    
    def clean(self):
        # TODO: should check question type against number of 
        # correct answers selected in AnswerInline
        return self.cleaned_data

class QuestionAdmin(admin.ModelAdmin):
    inlines = [AnswersInline,TagsInline]
    form = QuestionForm
    exclude = ('tags',)
    
admin.site.register(models.Question, QuestionAdmin)
admin.site.register(models.Tag)
