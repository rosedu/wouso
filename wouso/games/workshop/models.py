from datetime import datetime, time, timedelta
from django.db import models
from django.template.loader import render_to_string
from wouso.core.game.models import Game
from wouso.core.qpool.models import Tag, Question, Category
from wouso.core.user.models import PlayerGroup, Player

DAY_CHOICES = (
    (1, 'Monday'),
    (2, 'Tuesday'),
    (3, 'Wednesday'),
    (4, 'Thursday'),
    (5, 'Friday'),
)

class Schedule(Tag):
    """ Schedule qpool tags per date intervals.
    """
    start_date = models.DateField()
    end_date = models.DateField()

    @classmethod
    def get_current_tags(cls, timestamp=None):
        """ Return the questions tags currently active
        """
        timestamp = timestamp if timestamp else datetime.now()
        return cls.objects.filter(start_date__lte=timestamp, end_date__gte=timestamp)

    def is_active(self, timestamp=None):
        timestamp = timestamp if timestamp else datetime.now()
        return datetime.combine(self.start_date, time(0, 0, 0)) <= timestamp <= datetime.combine(self.end_date, time(23, 59, 59))

class Semigroup(PlayerGroup):
    class Meta:
        unique_together = ('day', 'hour')
    day = models.IntegerField(choices=DAY_CHOICES)
    hour = models.IntegerField(choices=zip(range(8, 22, 2), range(8, 22, 2)))

    def add_player(self, player):
        """ Add player to semigroup, remove it from any other semigroups.
        """
        for sg in Semigroup.objects.filter(players=player):
            sg.players.remove(player)

        self.players.add(player)

    @classmethod
    def get_by_day_and_hour(cls, day, hour):
        try:
            return cls.objects.get(day=day, hour=hour)
        except cls.DoesNotExist:
            return None

class Workshop(models.Model):
    semigroup = models.ForeignKey(Semigroup)
    date = models.DateField(auto_now_add=True)
    active_until = models.DateTimeField(blank=True, null=True)

    questions = models.ManyToManyField(Question, blank=True)

    def is_active(self, timestamp=None):
        timestamp = timestamp if timestamp else datetime.now()
        if not self.active_until:
            return False

        return self.active_until >= timestamp

    def __unicode__(self):
        return u"#%d - on %s" % (self.pk, self.date)

class Assesment(models.Model):
    workshop = models.ForeignKey(Workshop)
    player = models.ForeignKey(Player, related_name='assesments')

    answered = models.BooleanField(default=False, blank=True)
    time_start = models.DateTimeField(auto_now_add=True)
    time_end = models.DateTimeField(blank=True, null=True)

    reviewers = models.ManyToManyField(Player, blank=True, related_name='assesments_review')
    grade = models.IntegerField(blank=True, null=True)

    def set_answered(self, answers):
        """ Set given answer dictionary.
        """
        for q in self.workshop.questions.all():
            a = Answer.objects.get_or_create(assesment=self, question=q)[0]
            a.text = answers.get(q.id, '')
            a.save()
        self.answered = True
        self.time_end = datetime.now()
        self.save()

    @classmethod
    def get_for_player_and_workshop(cls, player, workshop):
        try:
            return cls.objects.get(player=player, workshop=workshop)
        except:
            return None

    __unicode__ = lambda self: u"#%d" % self.id

class Answer(models.Model):
    assesment = models.ForeignKey(Assesment)
    question = models.ForeignKey(Question)

    text = models.TextField(max_length=2000)
    grade = models.IntegerField(blank=True, null=True)

    __unicode__ = lambda self: self.text

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
    def get_question_pool(cls, timestamp=None):
        """ Return the questionpool active right now
        """
        tags = Schedule.get_current_tags(timestamp=timestamp)
        questions = Question.objects.filter(tags__in=tags).distinct()
        return questions

    @classmethod
    def get_for_now(cls, timestamp=None, always=True):
        """ Return an workshop object or None.

        Workshops are selected randomly from database.
        """
        # current semigroup
        semigroup = cls.get_semigroup(timestamp=timestamp)

        if not semigroup:
            return None

        # current tags and questions
        questions = cls.get_question_pool(timestamp=timestamp)

        if not questions:
            return None

        # Now decide if there is an workshop this week for this semigroup
        # TODO: magic. for now, always create one
        if always:
            return cls.get_or_create_workshop(semigroup, timestamp.date() if timestamp else datetime.today(), questions)
        return None

    @classmethod
    def get_for_player_now(cls, player, timestamp=None):
        semigroup = cls.get_semigroup(timestamp=timestamp)
        if semigroup and player in semigroup.players.all():
            return cls.get_for_now(timestamp=timestamp)
        return None

    @classmethod
    def get_or_create_workshop(cls, semigroup, date, questions):
        workshop, is_new = Workshop.objects.get_or_create(semigroup=semigroup, date=date)
        if is_new:
            for q in questions:
                workshop.questions.add(q)

            workshop.active_until = datetime.now() + timedelta(minutes=3)
            workshop.save()

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

    @classmethod
    def get_question_category(cls):
        return Category.objects.get_or_create(name='workshop')[0]

    @classmethod
    def get_sidebar_widget(cls, request):
        semigroup = cls.get_semigroup()
        workshop = cls.get_for_player_now(request.user.get_profile())
        sm = request.user.get_profile() in semigroup.players.all() if semigroup else False

        return render_to_string('workshop/sidebar.html',
                {'semigroup': semigroup, 'workshop': workshop, 'semigroup_member': sm})
