from django.db import models
from django.contrib.auth.models import User

def validate_dynq_code():
    # TODO: code should be validate here so we don't break the site
    # by executing bad code
    pass

class Tag(models.Model):
    name = models.CharField(max_length=256)
    # tags could have different types ("date" for questions tagged with a date for qotd)
    type = models.CharField(max_length=256, default="default")

    def __unicode__(self):
        return self.name + " (" + self.type + ")"

class Question(models.Model):
    text = models.TextField()
    proposed_by = models.ForeignKey(User, related_name="%(app_label)s_%(class)s_proposedby_related")
    endorsed_by = models.ForeignKey(User, null=True, blank=True, related_name="%(app_label)s_%(class)s_endorsedby_related")
    active = models.BooleanField(default=False)

    tags = models.ManyToManyField(Tag, blank=True, related_name="%(app_label)s_%(class)s_related")
    answer_type = models.CharField(max_length=1, choices=(("R", "single choice"), ("C", "multiple choice")), default="R")
    # a dynamic question would have its code run before returning it to the caller
    type = models.CharField(max_length=1, choices=(("S", "static"), ("D", "dynamic")), default="S")
    code = models.TextField(blank=True, validators=[validate_dynq_code], 
                            help_text="Use %text for initial text, %user for the user that sees the question.")

    def is_valid(self):
        if self.answers.count() == 0:
            return False
        if self.answers.filter(correct=True).count() == 0:
            return False
        return True
    
    def add_tag(self, tag):
        if not isinstance(tag, Tag):
            tag = Tag.objects.create(name=tag)
            tag.save()
        return self.tags.add(tag)
        
    def has_tag(self, tag):
        if not isinstance(tag, Tag):
          try:
              tag = Tag.objects.get(name=tag)
          except Tag.DoesNotExist:
              return False
        return tag in self.tags.all()
    
    def __unicode__(self):
        tags = [t for t in self.tags.all()]
        res = unicode(self.text) + " ["
        
        # no tags assigned to the question
        if not tags:
            return self.text
        
        for t in tags:
            res += str(t) + ", "
        
        return res[:-2] + "]"
    
class Answer(models.Model):
    question = models.ForeignKey(Question, related_name="answers")
    text = models.TextField()
    explanation = models.TextField(null=True, default='', blank=True)
    correct = models.BooleanField()
    
    def __unicode__(self):
        return self.text
