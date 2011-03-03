from django.db import models
from django.contrib.auth.models import User

class Tag(models.Model):
    name = models.CharField()
    # tags could have different types ("date" for questions tagged with a date for qotd)
    type = models.CharField(default="default")
    
class Question(models.Model):
    text = models.TextField()
    proposedby = models.ForeignKey(User, related_name="%(app_label)s_%(class)s_related")
    endorsedby = models.ForeignKey(User, null=True, related_name="%(app_label)s_%(class)s_related")
    active = models.BooleanField()
    tags = models.ManyToManyField(Tag)
    # a dynamic question would have its code run before returning it to the caller
    type = models.CharField(max_length=1, choices=(("S", "static"), ("D", "dynamic")))
    code = models.TextField(blank=True)
    
    class Meta:
        abstract = True

class RadioQuestion(Question):
    pass

class CheckQuestion(Question):
    pass