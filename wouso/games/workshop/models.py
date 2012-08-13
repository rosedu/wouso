from datetime import datetime
from django.db import models
from wouso.core.game.models import Game
from wouso.core.qpool.models import Tag, Question
from wouso.core.user.models import PlayerGroup, Player

DAY_CHOICES = (
    (1, 'Monday'),
    (2, 'Tuesday'),
    (3, 'Wednesday'),
    (4, 'Thursday'),
    (5, 'Friday'),
)

class Schedule(models.Model):
    """ Schedule qpool tags per date intervals.
    """
    tag = models.ForeignKey(Tag)
    start_date = models.DateField()
    end_date = models.DateField()

    @classmethod
    def get_current_tags(cls, timestamp=None):
        """ Return the questions tags currently active
        """
        timestamp = timestamp if timestamp else datetime.now()
        return Tag.objects.filter(schedule__start_date__lte=timestamp, schedule__end_date__gte=timestamp)

class Semigroup(PlayerGroup):
    class Meta:
        unique_together = ('day', 'hour')
    day = models.IntegerField(choices=DAY_CHOICES)
    hour = models.IntegerField(choices=zip(range(8, 22, 2), range(8, 22, 2)))

    @classmethod
    def get_by_day_and_hour(cls, day, hour):
        try:
            return cls.objects.get(day=day, hour=hour)
        except cls.DoesNotExist:
            return None

class Workshop(models.Model):
    semigroup = models.ForeignKey(Semigroup)
    date = models.DateField(auto_now_add=True)

    questions = models.ManyToManyField(Question, blank=True)

class Assesment(models.Model):
    workshop = models.ForeignKey(Workshop)
    player = models.ForeignKey(Player, related_name='assesments')

    reviewers = models.ManyToManyField(Player, blank=True, related_name='assesments_review')
    grade = models.IntegerField(blank=True, null=True)

class Answer(models.Model):
    assesment = models.ForeignKey(Assesment)
    question = models.ForeignKey(Question)

    text = models.TextField(max_length=2000)
    grade = models.IntegerField(blank=True, null=True)

class Review(models.Model):
    answer = models.ForeignKey(Answer)
    reviewer = models.ForeignKey(Player)

    feedback = models.TextField(max_length=2000)
    answer_grade = models.IntegerField()

    review_reviewer = models.ForeignKey(Player, related_name='reviews')
    review_grade = models.IntegerField(blank=True, null=True)

class WorkshopGame(Game):
    class Meta:
        proxy = True

    def __init__(self, *args, **kwargs):
        self._meta.get_field('verbose_name').default = "Workshop"
        self._meta.get_field('short_name').default = ""
        # the url field takes as value only a named url from module's urls.py
        self._meta.get_field('url').default = "workshop_index_view"
        super(WorkshopGame, self).__init__(*args, **kwargs)

    @classmethod
    def get_spot(cls, timestamp=None):
        """ Return the current laboratory as a day, hour pair
        """
        timestamp = timestamp if timestamp else datetime.now()
        day = timestamp.weekday() + 1 # 1 = Monday, etc
        hour = timestamp.hour - timestamp.hour % 2 # First lab starts at 8:00 AM
        return day, hour

    @classmethod
    def get_semigroup(cls, timestamp=None):
        """ Return the semigroup having a laboratory right now.
        """
        day, hour = cls.get_spot(timestamp)
        return Semigroup.get_by_day_and_hour(day, hour)

    @classmethod
    def get_for_now(cls, timestamp=None, always=False):
        """ Return an workshop object or None.

        Workshops are selected randomly from database.
        """
        # current semigroup
        semigroup = cls.get_semigroup(timestamp=timestamp)

        if not semigroup:
            return None

        # current tags and questions
        tags = Schedule.get_current_tags(timestamp=timestamp)
        questions = Question.objects.filter(tags__in=tags).distinct()

        if not questions:
            return None

        # Now decide if there is an workshop this week for this semigroup
        # TODO: magic. for now, always create one
        if always:
            return cls.get_or_create_workshop(semigroup, timestamp.date(), questions)
        return None

    @classmethod
    def get_or_create_workshop(cls, semigroup, date, questions):
        workshop = Workshop.objects.get_or_create(semigroup=semigroup, date=date)[0]
        for q in questions:
            workshop.questions.add(q)

        return workshop

    @classmethod
    def start_reviewing(cls, workshop):
        """ Set the reviewers for all assesments in this workshop
        """
        participating_players = [a.player for a in workshop.assesment_set.all()]

        # TODO: magic, now only rotate
        pp_rotated = [participating_players[-1]] + participating_players[:-1]
        for i,a in enumerate(workshop.assesment_set.all()):
            a.reviewers.add(pp_rotated[i])

    @classmethod
    def get_player_info(cls, player, workshop):
        """
        Return information regarding specific workshop for the player
        """
        participated = Assesment.objects.filter(player=player, workshop=workshop).count() > 0

        reviews = Review.objects.filter(answer__assesment__workshop=workshop, reviewer=player)
        expected_reviews = Answer.objects.filter(assesment__in=player.assesments_review.all())

        done = reviews.count() == expected_reviews.count()

        return dict(participated=participated, reviews=reviews, expected_reviews=expected_reviews,
                    done=done)