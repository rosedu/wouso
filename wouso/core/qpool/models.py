from random import shuffle
from datetime import datetime, date, timedelta

from django.db import models
from django.contrib.auth.models import User

from utils import validate_dynq_code
from ckeditor.fields import RichTextField

from wouso.core.common import Item


class Category(Item, models.Model):
    """ One to many grouping for Question objects. Usually a game
    defines it's own category of questions in qpool.
    """
    name = models.CharField(max_length=100, unique=True)


class Tag(models.Model):
    """ A simple way of grouping Questions """
    name = models.CharField(max_length=256)
    active = models.BooleanField(default=False)
    category = models.ForeignKey('Category', blank=True, null=True)

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
        self.question_set.update(active=True)

    def set_inactive(self):
        """ Same as activating, updates all Question objects with the
        tag
        """
        if self.active is False:
            return
        self.active = False
        self.save()
        self.question_set.update(active=False)


class Question(models.Model):
    """ A question in a qpool has text and a variable number of answers,
    category and tags, proposing and endorsing user.

    Dynamic questions also store a validation code, that run against
    the given answer should return True or False if the answer is valid.
    """
    text = models.TextField(null=True, blank=True, default="")
    rich_text = RichTextField(null=True, blank=True, default="")
    proposed_by = models.ForeignKey(User, null=True, blank=True, related_name="%(app_label)s_%(class)s_proposedby_related")
    endorsed_by = models.ForeignKey(User, null=True, blank=True, related_name="%(app_label)s_%(class)s_endorsedby_related")
    active = models.BooleanField()

    category = models.ForeignKey(Category, null=True)
    tags = models.ManyToManyField(Tag, blank=True)

    answer_type = models.CharField(max_length=1, choices=(("C", "multiple choice"), ("R", "single choice"),
                                   ("F", "free text")), default="C")
    # a dynamic question would have its code run before returning it to the caller
    type = models.CharField(max_length=1, choices=(("S", "static"), ("D", "dynamic")), default="S")
    code = models.TextField(blank=True, validators=[validate_dynq_code],
                            help_text="Use %text for initial text, %user for the user that sees the question.")

    date_added = models.DateTimeField(auto_now_add=True)
    date_changed = models.DateTimeField(auto_now=True)

    @property
    def answer(self):
        """ First answer, useful for quests, where there is only one answer allowed
        """
        try:
            return Answer.objects.filter(question=self).all()[0]
        except Answer.DoesNotExist, IndexError:
            return None

    @property
    def answers_all(self):
        """ A list of all answers """
        return self.answer_set.all()

    @property
    def answers(self):
        """ A list of all active answers """
        return self.answer_set.filter(active=True)

    @property
    def correct_answers(self):
        """ A list of all correct active answers """
        return self.answer_set.filter(active=True, correct=True)

    @property
    def shuffled_answers(self):
        """ A list of permuted answers, for displaying
        """
        if self.answers is None:
            return []
        answers = list(self.answers)
        shuffle(answers)
        return answers

    @property
    def day(self):
        """ The scheduled date for question, or None """
        try:
            return self.schedule.day
        except Schedule.DoesNotExist:
            return None

    def is_valid(self):
        """ At least one answer is required for questions other than free text.
        Also check for one correct answer """
        if self.answer_type == 'F':
            return bool(self.text)

        if not self.answers.count():
            return False
        if not self.answers.filter(correct=True).count():
            return False
        return True

    @property
    def tags_nice(self):
        """ Tags as a string """
        ret = ''

        if not self.tags.all():
            return ret

        for t in self.tags.all():
            ret += str(t) + ", "

        return ret[:-2]

    @property
    def scheduled(self):
        """ Day as a string """
        return str(self.day) if self.day else '-'

    def set_active(self, active=True):
        self.active = active
        self.save()
        return self.active

    def __unicode__(self):
        return self.text if self.text else self.rich_text


class Answer(models.Model):
    question = models.ForeignKey(Question)
    text = models.TextField()
    rich_text = RichTextField(null=True, blank=True)
    explanation = models.TextField(null=True, default='', blank=True)
    correct = models.BooleanField()
    active = models.BooleanField(default=True)

    def __unicode__(self):
        return self.text if self.text else self.rich_text


class Schedule(models.Model):
    question = models.OneToOneField(Question, related_name="schedule")
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
