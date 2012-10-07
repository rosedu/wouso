from random import shuffle
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

ROOM_CHOICES = (
    ('eg306', 'EG306'),
    ('eg106', 'EG106'),
)

class Schedule(Tag):
    """ Schedule qpool tags per date intervals.
    """
    start_date = models.DateField(default=datetime.today)
    end_date = models.DateField(default=datetime.today)

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
        unique_together = ('day', 'hour', 'room')
    day = models.IntegerField(choices=DAY_CHOICES)
    hour = models.IntegerField(choices=zip(range(8, 22, 2), range(8, 22, 2)))
    room = models.CharField(max_length=5, default='eg306', choices=ROOM_CHOICES, blank=True)

    @property
    def info(self):
        return "spot: %s %d:00 room: %s" % (self.get_day_display(), self.hour, self.get_room_display())

    def add_player(self, player):
        """ Add player to semigroup, remove it from any other semigroups.
        """
        for sg in Semigroup.objects.filter(players=player):
            sg.players.remove(player)

        self.players.add(player)

    @classmethod
    def get_by_player(cls, player):
        try:
            return Semigroup.objects.filter(players=player).all()[0]
        except:
            return None

    @classmethod
    def get_by_day_and_hour(cls, day, hour):
        """
         Returns a list of groups in that timespan
        """
        qs = cls.objects.filter(day=day, hour=hour)
        if qs.count():
            return list(qs)

        return [cls.objects.get_or_create(day=0, hour=0, name='default', owner=WorkshopGame.get_instance())[0]]

class Workshop(models.Model):
    STATUSES = (
        (0, 'Ready'),
        (1, 'Reviewing'),
        (2, 'Grading'),
        (3, 'Archived'),
    )
    semigroup = models.ForeignKey(Semigroup)
    date = models.DateField(default=datetime.today)
    start_at = models.DateTimeField(blank=True, null=True)
    active_until = models.DateTimeField(blank=True, null=True)
    status = models.IntegerField(choices=STATUSES, default=0)
    question_count = models.IntegerField(default=4, blank=True)

    def is_started(self):
        return self.status == 0

    def is_ready(self):
        return self.status == 0

    def is_active(self, timestamp=None):
        timestamp = timestamp if timestamp else datetime.now()
        if not self.active_until:
            return False

        return self.active_until >= timestamp

    def is_reviewable(self):
        return self.status == 1

    def is_gradable(self):
        return self.status == 2

    def set_gradable(self):
        self.status = 2
        self.save()

    def get_or_create_assessment(self, player):
        """ Return existing or new assessment for player
        """
        assessment, is_new = Assessment.objects.get_or_create(player=player, workshop=self)
        if is_new:
            questions = list(WorkshopGame.get_question_pool(self.date))
            shuffle(questions)
            for q in questions[:self.question_count]:
                assessment.questions.add(q)
        return assessment

    def start(self, timestamp=None):
        timestamp = timestamp if timestamp else datetime.now()

        if self.is_ready():
            self.start_at = timestamp
            self.active_until = timestamp + timedelta(minutes=15)
            self.save()
            return True

        return False

    def stop(self):
        if self.active_until > datetime.now():
            self.active_until = datetime.now() - timedelta(seconds=1)
            self.save()
            return True
        return False

    def __unicode__(self):
        return u"#%d - on %s" % (self.pk, self.date)

class Assessment(models.Model):
    workshop = models.ForeignKey(Workshop)
    player = models.ForeignKey(Player, related_name='assessments')
    questions = models.ManyToManyField(Question, blank=True)

    answered = models.BooleanField(default=False, blank=True)
    time_start = models.DateTimeField(auto_now_add=True)
    time_end = models.DateTimeField(blank=True, null=True)

    reviewers = models.ManyToManyField(Player, blank=True, related_name='assessments_review')
    grade = models.IntegerField(blank=True, null=True)
    reviewer_grade = models.IntegerField(blank=True, null=True)
    final_grade = models.IntegerField(blank=True, null=True)

    def set_answered(self, answers):
        """ Set given answer dictionary.
        """
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
        reviewer_grade = self.player.review_set.filter(answer__assessment=self).aggregate(grade=models.Sum('review_grade'))['grade']
        self.reviewer_grade = reviewer_grade
        try:
            self.final_grade = (self.grade + self.reviewer_grade)/2
        except TypeError: # one of the grades is None
            self.final_grade = None
        self.save()

    @classmethod
    def get_for_player_and_workshop(cls, player, workshop):
        try:
            return cls.objects.get(player=player, workshop=workshop)
        except cls.DoesNotExist:
            return None

    __unicode__ = lambda self: u"#%d" % self.id

class Answer(models.Model):
    assessment = models.ForeignKey(Assessment)
    question = models.ForeignKey(Question, related_name='wsanswers')

    text = models.TextField(max_length=2000)
    grade = models.IntegerField(blank=True, null=True)

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
    def get_spot(cls, timestamp=None):
        """ Return the current laboratory as a day, hour pair
        """
        timestamp = timestamp if timestamp else datetime.now()
        day = (timestamp.weekday() + 1) % 7 + 1 # 1 = Monday, etc
        hour = timestamp.hour - timestamp.hour % 2 # First lab starts at 8:00 AM
        return day, hour

    @classmethod
    def get_semigroup(cls, timestamp=None):
        """ Return the semigroup list having a laboratory right now.
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
    def get_for_now(cls, timestamp=None):
        """ Return a list of semigroups and workshops, or None if there isn't any workshop available.

        Workshops are selected randomly from database.
        """
        day = timestamp.date() if timestamp else datetime.today()

        # current semigroup(s)
        semigroups = cls.get_semigroup(timestamp=timestamp)

        result = []
        for s in semigroups:
            result.append({'semigroup': s, 'workshop': cls.get_workshop(s, day)})

        return result

    @classmethod
    def get_for_player_now(cls, player, timestamp=None):
        timestamp = timestamp if timestamp else datetime.now()
        ws = Workshop.objects.filter(start_at__lte=timestamp, active_until__gte=timestamp)
        for w in ws:
            if player in w.semigroup.players.all():
                return w

        return None

    @classmethod
    def get_workshop(cls, semigroup, date):
        try:
            return Workshop.objects.get(semigroup=semigroup, date=date)
        except Workshop.DoesNotExist:
            return None

    @classmethod
    def create_workshop(cls, semigroup, date, question_count=4):
        """
         Creates an workshop instance.

         Returns: False if no error, string if error.
        """
        questions = cls.get_question_pool(date)

        if not questions or questions.count() < question_count:
            return "No questions for this date"

        if cls.get_workshop(semigroup, date):
            return "Workshop already exists for group at date"

        Workshop.objects.create(semigroup=semigroup, date=date, question_count=question_count)

        return False

    @classmethod
    def get_or_create_workshop(cls, semigroup, date, questions):
        workshop, is_new = Workshop.objects.get_or_create(semigroup=semigroup, date=date)
        if is_new:
            workshop.active_until = datetime.now() + timedelta(minutes=15)
            workshop.save()

        return workshop

    @classmethod
    def start_reviewing(cls, workshop):
        """ Set the reviewers for all assessments in this workshop
        """
        participating_players = [a.player for a in workshop.assessment_set.all()]

        # TODO: magic, now only rotate
        pp_rotated = [participating_players[-1]] + participating_players[:-1]
        for i,a in enumerate(workshop.assessment_set.all()):
            a.reviewers.clear()
            a.reviewers.add(pp_rotated[i])

        workshop.status = 1 # reviewing
        workshop.save()

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
    def get_sidebar_widget(cls, request):
        player = request.user.get_profile()
        semigroups = cls.get_semigroup()
        workshop = cls.get_for_player_now(player)
        assessment = Assessment.get_for_player_and_workshop(player, workshop)
        sm = False
        for sg in semigroups:
            if player in sg.players.all():
                sm = True
                break

        return render_to_string('workshop/sidebar.html',
                {'semigroups': semigroups, 'workshop': workshop, 'semigroup_member': sm, 'assessment': assessment})
