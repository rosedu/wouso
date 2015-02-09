from math import ceil
from random import shuffle
from datetime import datetime, time, timedelta
from django.db import models
from django.template.loader import render_to_string
from django.utils.translation import ugettext as _
from django.conf import settings
from wouso.core.game.models import Game
from wouso.core.qpool.models import Tag, Question, Category
from wouso.core.ui import register_sidebar_block
from wouso.core.user.models import PlayerGroup, Player
from wouso.interface.apps.messaging.models import Message

DAY_CHOICES = (
    (1, 'Monday'),
    (2, 'Tuesday'),
    (3, 'Wednesday'),
    (4, 'Thursday'),
    (5, 'Friday'),
#    (6, 'Saturday'),
#    (7, 'Sunday'),
)

ROOM_CHOICES = (
    ('eg306', 'EG306'),
    ('eg106', 'EG106'),
    ('ef108', 'EF108'),
)

ROOM_DEFAULT = 'eg306'

MIN_HOUR, MAX_HOUR = 8, 22


class Schedule(Tag):
    """ Schedule qpool tags per date intervals.
    TODO: move it to qpool
    """
    start_date = models.DateField(default=datetime.today)
    end_date = models.DateField(default=datetime.today)
    count = models.IntegerField(default=3, help_text='How many questions of this tag to select')

    @classmethod
    def get_current_tags(cls, timestamp=None):
        """ Return the questions tags currently active
        """
        timestamp = timestamp if timestamp else datetime.now()
        return cls.objects.filter(start_date__lte=timestamp, end_date__gte=timestamp).order_by('name')

    def is_active(self, timestamp=None):
        timestamp = timestamp if timestamp else datetime.now()
        return datetime.combine(self.start_date, time(0, 0, 0)) <= timestamp <= datetime.combine(self.end_date, time(23, 59, 59))


class WorkshopPlayer(Player):
    _semigroup = None

    @property
    def semigroup(self):
        if self._semigroup is not None:
            return self._semigroup

        self._semigroup = Semigroup.get_by_player(self)
        return self._semigroup


class Semigroup(PlayerGroup):
    class Meta:
        unique_together = ('day', 'hour', 'room')
    day = models.IntegerField(choices=DAY_CHOICES)
    hour = models.IntegerField(choices=zip(range(MIN_HOUR, MAX_HOUR, 2),
                                           range(MIN_HOUR, MAX_HOUR, 2)))
    room = models.CharField(max_length=5, default=ROOM_DEFAULT,
                            choices=ROOM_CHOICES, blank=True)
    assistant = models.ForeignKey(Player, blank=True, null=True,
                                  related_name='semigroups')

    @property
    def info(self):
        return "spot: %s %d:00 room: %s" % (
            self.get_day_display(), self.hour, self.get_room_display()
        )

    def add_player(self, player):
        """ Add player to semigroup, remove it from any other semigroups.
        """
        for sg in Semigroup.objects.filter(players=player):
            sg.players.remove(player)

        self.players.add(player)

    @classmethod
    def get_by_player(cls, player):
        try:
            return Semigroup.objects.filter(players__id=player.id).all()[0]
        except IndexError:
            return None


class Workshop(models.Model):
    STATUSES = (
        (0, 'Ready'),
        (1, 'Reviewing'),
        (2, 'Grading'),
        (3, 'Archived'),
    )
    semigroup = models.ForeignKey(Semigroup)
    date = models.DateField(default=datetime.today)
    title = models.CharField(max_length=128, default='', blank=True)
    start_at = models.DateTimeField(blank=True, null=True)
    active_until = models.DateTimeField(blank=True, null=True)
    status = models.IntegerField(choices=STATUSES, default=0)
    question_count = models.IntegerField(default=3, blank=True)

    def is_started(self):
        return self.status == 0

    def is_ready(self):
        return self.status == 0

    def is_active(self, timestamp=None):
        timestamp = timestamp if timestamp else datetime.now()
        timestamp2 = timestamp - timedelta(minutes=settings.WORKSHOP_GRACE_PERIOD)
        if not self.start_at or not self.active_until:
            return False

        return self.start_at <= timestamp and timestamp2 <= self.active_until

    def is_passed(self, timestamp=None):
        timestamp = timestamp if timestamp else datetime.now()
        if not self.active_until:
            return False

        return timestamp > self.active_until

    def is_reviewable(self):
        return self.status == 1

    def is_gradable(self):
        return self.status == 2

    def set_gradable(self):
        self.status = 2
        self.save()

    def get_assessment(self, player):
        """
        Return existing assesment for player
        """
        try:
            return Assessment.objects.get(player=player, workshop=self)
        except Assessment.DoesNotExist:
            return None
        except Assessment.MultipleObjectsReturned:
            return Assessment.objects.filter(player=player, workshop=self).order_by('id')[0]

    def get_or_create_assessment(self, player):
        """ Return existing or new assessment for player
        """
        try:
            assessment, is_new = Assessment.objects.get_or_create(player=player, workshop=self)
        except Assessment.MultipleObjectsReturned:
            assessment, is_new = Assessment.objects.filter(player=player, workshop=self).order_by('id')[0], False

        if is_new:
            total_count = self.question_count
            for count, questions in WorkshopGame.get_question_pool(self.date):
                questions = list(questions)
                shuffle(questions)
                for q in questions[:count]:
                    assessment.questions.add(q)
                total_count -= count
                if total_count <= 0:
                    break
        return assessment

    def start(self, timestamp=None):
        """ Start a workshop if it's ready.
        """
        timestamp = timestamp if timestamp else datetime.now()

        if self.is_ready():
            self.start_at = timestamp
            self.active_until = timestamp + timedelta(minutes=settings.WORKSHOP_TIME_MINUTES)
            self.save()
            return True

        return False

    def stop(self):
        if self.is_active():
            self.active_until = datetime.now() - timedelta(seconds=1)
            self.save()
            return True
        return False

    @property
    def integrity(self):
        return reduce(lambda b, a: b and a.integrity, self.assessment_set.all(), True)

    def __unicode__(self):
        return u"%s - %s [#%d]" % (self.title, self.date, self.pk)


class Assessment(models.Model):
    workshop = models.ForeignKey(Workshop)
    player = models.ForeignKey(Player, related_name='assessments')
    questions = models.ManyToManyField(Question, blank=True)

    answered = models.BooleanField(default=False, blank=True)
    time_start = models.DateTimeField(auto_now_add=True)
    time_end = models.DateTimeField(blank=True, null=True)

    reviewers = models.ManyToManyField(Player, blank=True, related_name='assessments_review')
    grade = models.IntegerField(blank=True, null=True, help_text='Grade given by assistant')
    reviewer_grade = models.IntegerField(blank=True, null=True, help_text='Grade given to player, as a reviewer to other assesments')
    final_grade = models.IntegerField(blank=True, null=True, help_text='Mean value, grade+reviewer_grade')

    @property
    def reviews_grade(self):
        """
        Return the grade given to this Assessment from reviews
        """
        reviews_count = self.reviewers.count()
        sum = Review.objects.filter(answer__assessment=self, reviewer__in=self.reviewers.all()).aggregate(sum=models.Sum('answer_grade'))['sum']
        if sum is None:
            return None
        return int(sum/reviews_count) if reviews_count else 0

    def set_answered(self, answers=None):
        """ Set given answer dictionary.
        """
        answers = answers if answers else {}

        for q in self.questions.all():
            a = Answer.objects.get_or_create(assessment=self, question=q)[0]
            a.text = answers.get(q.id, '')
            a.save()
        self.answered = True
        self.time_end = datetime.now()
        self.save()

    def update_grade(self):
        """ Set grade as sum of every answer final grade
        """
        grade = Answer.objects.filter(assessment=self).aggregate(grade=models.Sum('grade'))['grade']
        self.grade = grade
        reviewer_grade = self.player.review_set.filter(answer__assessment__workshop=self.workshop).aggregate(grade=models.Sum('review_grade'))['grade']
        if reviewer_grade is None:
            self.reviewer_grade = 0
        else:
            self.reviewer_grade = reviewer_grade

        # Special case: one of the reviewed was empty: will point it as it is
        if self.reviews.filter(answered=True).count() == 1:
            self.reviewer_grade *= 2

        count = self.questions.count()
        try:
            """
             Formula:
                (grade * 10 + reviewer * 5) / 16 - when there are 4 questions
                max(grade) = 8
                max(reviewer) = 16
                8 * 10 + 16 * 5 / 16 = 10 = max(final_grade)
            """
            self.final_grade = ceil((self.grade * 10 + self.reviewer_grade * 5) * 1.0 / (4 * count))
        except (ZeroDivisionError, TypeError): # one of the grades is None
            self.final_grade = None
        self.save()

    def time_left(self):
        """
         Return time left in seconds or 0 if passed
        """
        if not self.workshop.is_started():
            return -1

        if not self.workshop.active_until:
            return -2

        now = datetime.now()

        return (self.workshop.active_until - now).seconds

    @property
    def reviews(self):
        """
         Return the assessments that this player gave reviews in the same workshop as this assessment
        """
        return self.player.assessments_review.filter(workshop=self.workshop)

    @property
    def real_reviewers(self):
        """
         Return a set of users from reviews
        """
        rr = Player.objects.filter(id__in=Review.objects.filter(answer__assessment=self).values('reviewer'))
        return [r for r in rr if not r.in_staff_group()]

    @property
    def integrity(self):
        r_ids = [int(a[0]) for a in self.reviewers.all().values_list('id')]
        for r in self.real_reviewers:
            if r.id not in r_ids:
                return False

        return True

    def remove_non_expected_reviews(self):
        for a in self.answer_set.all():
            for r in a.review_set.all():
                if r.reviewer not in list(self.reviewers.all()) and not r.reviewer.in_staff_group():
                    r.delete()

    __unicode__ = lambda self: u"#%d" % self.id


class Answer(models.Model):
    assessment = models.ForeignKey(Assessment)
    question = models.ForeignKey(Question, related_name='wsanswers')

    text = models.TextField(max_length=2000)
    grade = models.IntegerField(blank=True, null=True)

    def set_grade(self, grade):
        """
         Only an assistant can set the grade.
        """
        self.grade = grade
        self.save()

    def add_review(self, reviewer, feedback, grade=None):
        """
         Add a text review to this answer. Called by assistant or regular player
        """
        review = Review.objects.get_or_create(answer=self, reviewer=reviewer)[0]
        review.feedback = feedback
        review.answer_grade = grade
        review.save()
        return review

    @property
    def reviewers(self):
        return Player.objects.filter(id__in=Review.objects.filter(answer=self).values('reviewer'))

    __unicode__ = lambda self: self.text


class Review(models.Model):
    answer = models.ForeignKey(Answer)
    reviewer = models.ForeignKey(Player)

    feedback = models.TextField(max_length=2000, blank=True, null=True)
    answer_grade = models.IntegerField(blank=True, null=True)

    review_reviewer = models.ForeignKey(Player, related_name='reviews', blank=True, null=True)
    review_grade = models.IntegerField(blank=True, null=True)

    # Properties and methods
    def set_grade(self, assistant, grade):
        """ Only an assistant can grade a review
        """
        self.review_grade = grade
        self.review_reviewer = assistant
        self.save()

    workshop = property(lambda self: self.answer.assessment.workshop)

    __unicode__ = lambda self: u"%s by %s" % (self.feedback, self.reviewer)


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
    def get_staff_and_permissions(cls):
        return [{'name': 'Workshop Staff', 'permissions': ['change_semigroup']}]

    @classmethod
    def default_room(cls):
        return ROOM_DEFAULT

    @classmethod
    def get_spot(cls, timestamp=None):
        """ Return the current laboratory as a day, hour pair
        """
        timestamp = timestamp if timestamp else datetime.now()
        day = timestamp.weekday() + 1 # 1 = Monday, etc
        hour = timestamp.hour - timestamp.hour % 2 # First lab starts at 8:00 AM
        return day, hour

    @classmethod
    def get_semigroups(cls, timestamp=None):
        """ Return the semigroups list having a laboratory right now.
        """
        day, hour = cls.get_spot(timestamp)
        return cls.get_by_day_and_hour(day, hour)

    @classmethod
    def get_by_day_and_hour(cls, day, hour):
        """
         Returns a list of groups in that time span
        """
        qs = Semigroup.objects.filter(day=day, hour=hour)
        if qs.count():
            return list(qs)

        return [Semigroup.objects.get_or_create(day=0, hour=0, name='default', owner=cls.get_instance())[0]]

    @classmethod
    def get_question_pool(cls, timestamp=None):
        """ Return the question pool active right now as a list of querysets and and counts to be used
        """
        tags = Schedule.get_current_tags(timestamp=timestamp)
        result = []
        for t in tags:
            result.append((t.count, t.question_set.all()))
        return result

    @classmethod
    def get_for_now(cls, timestamp=None):
        """ Return a list of semigroups and workshops, or None if there isn't any workshop available.

        Workshops are selected randomly from database.
        """
        day = timestamp.date() if timestamp else datetime.today()

        # current semigroup(s)
        semigroups = cls.get_semigroups(timestamp=timestamp)

        result = []
        for s in semigroups:
            result.append({'semigroup': s, 'workshop': cls.get_workshop(s, day)})

        return result

    @classmethod
    def get_for_player_now(cls, player, timestamp=None):
        """
         Return existing workshop for a player, now.
        """
        if player.in_staff_group():
            return None
        timestamp = timestamp if timestamp else datetime.now()
        timestamp2 = timestamp - timedelta(minutes=settings.WORKSHOP_GRACE_PERIOD)
        ws = Workshop.objects.filter(start_at__lte=timestamp, active_until__gte=timestamp2)
        for w in ws:
            if player in w.semigroup.players.all():
                return w

        return None

    @classmethod
    def get_workshop(cls, semigroup, date):
        """
         Return existing workshop for a semigroup and a date.
        """
        try:
            return Workshop.objects.get(semigroup=semigroup, date=date)
        except Workshop.DoesNotExist:
            return None

    @classmethod
    def create_workshop(cls, semigroup, date, title, question_count=4):
        """
         Creates an workshop instance.

         Returns: False if no error, string if error.
        """
        #questions = cls.get_question_pool(date)
        #
        #if not questions or questions.count() < question_count:
        #    return _("No questions for this date")

        if cls.get_workshop(semigroup, date):
            raise ValueError(_("Workshop already exists for group at date"))

        return Workshop.objects.create(semigroup=semigroup, date=date,
                                       question_count=question_count,
                                       title=title)

    @classmethod
    def start_reviewing(cls, workshop):
        """ Set the reviewers for all assessments in this workshop
        """
        le_assessments = [a for a in list(workshop.assessment_set.filter(answered=True)) if not a.player.in_staff_group()]
        shuffle(le_assessments)

        participating_players = [a.player for a in le_assessments]

        if not participating_players:
            return

        pp_rotated = [participating_players[-1]] + participating_players[:-1]
        for i,a in enumerate(le_assessments):
            a.reviewers.clear()
            a.reviewers.add(pp_rotated[i])

        # If there are more than two players, do this again
        if len(participating_players) > 2:
            pp_rotated = participating_players[-2:] + participating_players[:-2]
            for i,a in enumerate(le_assessments):
                a.reviewers.add(pp_rotated[i])

        workshop.status = 1 # reviewing
        workshop.save()

        # send message to every player
        for player in participating_players:
            Message.send(None, player, _("Workshop to review!"),
                    _("Hello, the reviewing stage for the latest workshop has begun."))

    @classmethod
    def get_player_info(cls, player, workshop):
        """
        Return information regarding specific workshop for the player
        """
        participated = Assessment.objects.filter(player=player, workshop=workshop).count() > 0

        reviews = Review.objects.filter(answer__assessment__workshop=workshop, reviewer=player)
        expected_reviews = Answer.objects.filter(assessment__in=player.assessments_review.all())

        done = reviews.count() == expected_reviews.count()

        return dict(participated=participated, reviews=reviews, expected_reviews=expected_reviews,
                    done=done)

    @classmethod
    def get_question_category(cls):
        return Category.objects.get_or_create(name='workshop')[0]

    @classmethod
    def get_sidebar_widget(cls, context):
        user = context.get('user', None)
        if not user or user.is_anonymous():
            return ''

        if WorkshopGame.disabled():
            return ''

        player = user.get_profile()
        ws_player = player.get_extension(WorkshopPlayer)
        semigroups = cls.get_semigroups()
        workshop = cls.get_for_player_now(player)
        if workshop:
            assessment = workshop.get_assessment(player)
        else:
            assessment = None
        sm = ws_player.semigroup in semigroups

        return render_to_string('workshop/sidebar.html',
                {'semigroups': semigroups, 'workshop': workshop, 'semigroup_member': sm, 'assessment': assessment,
                 'id': 'workshop'})

register_sidebar_block('workshop', WorkshopGame.get_sidebar_widget)
