from datetime import datetime, date, timedelta
from django.db import models
from django.contrib.auth.models import User

def validate_dynq_code():
    # TODO: code should be validate here so we don't break the site
    # by executing bad code
    pass

class Tag(models.Model):
    """ A simple way of grouping Questions """
    name = models.CharField(max_length=256)
    active = models.BooleanField(default=False)

    def __unicode__(self):
        return self.name

    def set_active(self):
        """ Activating a tag implies activating all the Question objects
        having this tag.
        """
        if self.active is True:
            return
        self.active = True
        self.save()
        Question.objects.filter(tags__name=self.name).update(active=True)

    def set_inactive(self):
        """ Same as activating, updates all Question objects with the
        tag
        """
        if self.active is False:
            return
        self.active = False
        self.save()
        Question.objects.filter(tags__name=self.name).update(active=False)


class Category(models.Model):
    """ One to many grouping for Question objects. Usually a game
    defines it's own category of questions in qpool.
    """
    name = models.CharField(max_length=64)

    def __unicode__(self):
        return self.name

class Question(models.Model):
    """ A question in a qpool has text and a variable number of answers,
    category and tags, proposing and endorsing user.
    
    Dynamic questions also store a validation code, that run against
    the given answer should return True or False if the answer is valid.
    """
    text = models.TextField()
    proposed_by = models.ForeignKey(User, null=True, blank=True, related_name="%(app_label)s_%(class)s_proposedby_related")
    endorsed_by = models.ForeignKey(User, null=True, blank=True, related_name="%(app_label)s_%(class)s_endorsedby_related")
    active = models.BooleanField(default=False)

    category = models.ForeignKey(Category, null=True)
    tags = models.ManyToManyField(Tag, blank=True, related_name="%(app_label)s_%(class)s_related")
    answer_type = models.CharField(max_length=1, choices=(("R", "single choice"), ("C", "multiple choice")), default="R")
    # a dynamic question would have its code run before returning it to the caller
    type = models.CharField(max_length=1, choices=(("S", "static"), ("D", "dynamic")), default="S")
    code = models.TextField(blank=True, validators=[validate_dynq_code],
                            help_text="Use %text for initial text, %user for the user that sees the question.")

    @property
    def answers(self):
        """ A list of answers """
        try:
            return Answer.objects.filter(question=self).all()
        except Answer.DoesNotExist:
            return None

    @property
    def day(self):
        """ The scheduled date for question, or None """
        try:
            return Schedule.objects.filter(question=self)[0].day
        except (Schedule.DoesNotExist, IndexError):
            return None

    def is_valid(self):
        """ At least one answer is required. Also check for one correct
        answer """
        if self.answers.count() == 0:
            return False
        if self.answers.filter(correct=True).count() == 0:
            return False
        return True

    def add_tag(self, tag):
        """ Adding tag helper """
        # TODO check usage, rewrite or deprecate
        if not isinstance(tag, Tag):
            tag = Tag.objects.create(name=tag)
            tag.save()
        return self.tags.add(tag)

    def has_tag(self, tag):
        """ Has tag helper """
        # TODO check usage, rewrite or deprecate
        if not isinstance(tag, Tag):
            try:
                tag = Tag.objects.get(name=tag)
            except Tag.DoesNotExist:
                return False
        return tag in self.tags.all()

    @property
    def question(self):
        # TODO check usage
        return unicode(self.text)

    def tag(self):
        """ Tag as a string """
        # TODO rename
        tlist = self.tags.all()
        ret = ""

        # no tags assigned to the question
        if not tlist:
            return ''

        for t in tlist:
            ret += str(t) + ", "

        return ret[:-2]

    def scheduled(self):
        """ Day as a string """
        # TODO: rewrite using self.day
        slist = Schedule.objects.filter(question=self)
        ret = ""

        # no days scheduled for the question
        if not slist:
            return ''

        for s in slist:
            ret += str(s) + ", "

        return ret[:-2]

    def __unicode__(self):
        return unicode(self.text)

class Answer(models.Model):
    question = models.ForeignKey(Question, related_name="zanswers")
    text = models.TextField()
    explanation = models.TextField(null=True, default='', blank=True)
    correct = models.BooleanField()

    def __unicode__(self):
        return self.text

class Schedule(models.Model):
    question = models.ForeignKey(Question, related_name="schedule")
    day = models.DateField(default=datetime.now, blank=True)

    @classmethod
    def automatic(kls, qotd='qotd'):
        """ Automatically schedule all active questions on dates newer
        than the newest in database or today.

        Affects only questions in category qotd.
        """
        newest = Schedule.objects.aggregate(models.Max('day'))
        if not newest:
            return
        day = newest.get('day__max', date.today())
        if day is None:
            day = date.today() - timedelta(days=1)
        day += timedelta(days=1)

        for q in Question.objects.filter(active=True).filter(category__name=qotd).filter(schedule__isnull=True).order_by('id'):
            Schedule.objects.create(question=q, day=day)
            day = day + timedelta(days=1)

    def __unicode__(self):
        return str(self.day)
