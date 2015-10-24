import os
import pickle

from datetime import datetime
from random import shuffle

from django.conf import settings
from django.db import models
from django.utils.translation import ugettext as _

from wouso.core import scoring
from wouso.core.signals import add_activity
from wouso.core.user.models import Player
from wouso.core.game.models import Game
from wouso.core.qpool import register_category,\
get_questions_with_tag_and_category
from wouso.core.qpool.models import Question, Tag


class QuizCategory(models.Model):
    name = models.CharField(max_length=100, unique=True)
    logo = models.ImageField(upload_to=\
    	settings.MEDIA_ARTIFACTS_DIR, null=True, blank=True)

    @property
    def quizzes(self):
        return self.quiz_set.all()

    @property
    def logo_url(self):
        return os.path.join(settings.MEDIA_ARTIFACTS_URL,\
        os.path.basename(str(self.logo))) if self.logo else ""

    def __unicode__(self):
        return self.name


class Quiz(models.Model):
    CHOICES = {
        ('A', 'ACTIVE'),
        ('I', 'INACTIVE'),  # Active in future
        ('E', 'EXPIRED')
    }

    TYPES = {
        ('P', 'Public'),
        ('L', 'Lesson')
    }

    category = models.ForeignKey(QuizCategory, null=True, blank=True)

    name = models.CharField(max_length=100)
    time_limit = models.IntegerField(default=300)

    type = models.CharField(max_length=1, choices=TYPES)

    points_reward = models.IntegerField(default=100)
    gold_reward = models.IntegerField(default=30)

    tags = models.TextField(blank=True, null=True)

    start = models.DateTimeField()
    end = models.DateTimeField()

    another_chance = models.IntegerField(default=7)

    owner = models.ForeignKey(Game, null=True, blank=True)

    status = models.CharField(max_length=1, choices=CHOICES)

    def set_active(self):
        self.status = 'A'
        self.save()

    def set_inactive(self):
        self.status = 'I'
        self.save()

    def set_expired(self):
        self.status = 'E'
        self.save()

    def is_active(self):
        return self.status == 'A'

    def is_inactive(self):
        return self.status == 'I'

    def is_expired(self):
        return self.status == 'E'

    def is_public(self):
        return self.type == 'P'

    def update_status(self):
        now = datetime.now()
        if self.start <= now <= self.end:
            self.status = 'A'
        elif self.end < now:
            self.status = 'E'
        self.save()

    @property
    def qtype(self):
        if self.type == 'L':
            return 'Lesson'
        return 'Public'

    def calculate_reward(self, responses):
        """
         Response contains a dict with question id and checked answers ids.
         Example:
            {1 : [14,], ...}, - has answered answer
            with id 14 at the question with id 1
        """
        if len(responses) == 0:
            return 0, 0

        correct_count = 0.0
        total_count = len(responses)

        for question_id, checked_answer_id in responses.iteritems():
            question = Question.objects.get(id=question_id)
            correct_answer_id = [ans.id \
            for ans in question.answers if ans.correct]
            if checked_answer_id == correct_answer_id:
                correct_count += 1

        points = int((correct_count / total_count) * int(self.points_reward))
        gold = int((correct_count / total_count) * int(self.gold_reward))
        return points, gold

    def __unicode__(self):
        return self.name


class QuizGame(Game):
    """
     Each game must extend Game
    """

    class Meta:
        proxy = True

    QPOOL_CATEGORY = 'quiz'

    def __init__(self, *args, **kwargs):
        self._meta.get_field('verbose_name').default = "Quiz"
        self._meta.get_field('short_name').default = ""
        self._meta.get_field('url').default = "quiz_index_view"
        super(QuizGame, self).__init__(*args, **kwargs)


class QuizUser(Player):
    """
     Extension of the User object, customized for quiz
    """
    quizzes = models.ManyToManyField(Quiz, through='UserToQuiz')

    @property
    def active_quizzes(self):
        # Active public quizzes
        through = UserToQuiz.objects.filter(user=self)
        active_quizzes = [t for t in through \
        if t.quiz.is_active() and t.quiz.is_public()]
        return active_quizzes

    @property
    def inactive_quizzes(self):
        through = UserToQuiz.objects.filter(user=self)
        inactive_quizzes = [t for t in through \
        if t.quiz.is_inactive() and t.quiz.is_public()]
        return inactive_quizzes

    @property
    def expired_quizzes(self):
        through = UserToQuiz.objects.filter(user=self)
        expired_quizzes = [t for t in through if t.quiz.is_expired()]
        return expired_quizzes

    @property
    def played_quizzes(self):
        through = UserToQuiz.objects.filter(user=self, state='P')
        return through


Player.register_extension('quiz', QuizUser)

register_category(QuizGame.QPOOL_CATEGORY, QuizGame)


class UserToQuiz(models.Model):
    """
     Used as a link between each user and each quiz
    """
    CHOICES = {
        ('P', 'PLAYED'),
        ('R', 'RUNNING'),
        ('N', 'NOT RUNNING')
    }

    user = models.ForeignKey(QuizUser)
    quiz = models.ForeignKey(Quiz)
    questions = models.ManyToManyField(Question)
    state = models.CharField(max_length=1, choices=CHOICES, default='N')
    start = models.DateTimeField(blank=True, null=True)

    @property
    def all_attempts(self):
        return self.attempts.all()

    @property
    def best_attempt(self):
        if self.all_attempts.count() == 0:
            return None
        return sorted(self.all_attempts, \
        	key=lambda x: x.points, reverse=True)[0]

    @property
    def last_attempt(self):
        if self.all_attempts.count() == 0:
            return None
        return list(self.all_attempts)[-1]

    def make_questions(self):
        if self.questions.count() != 0:
            return

        t = pickle.loads(self.quiz.tags)
        questions = []
        for k in t:
            q = get_questions_with_tag_and_category(k, 'quiz')
            # Cannot shuffle a queryset, create list from it
            q = list(q)
            shuffle(q)
            for i in q[:t[k]]:
                questions.append(i)

        shuffle(questions)
        self.questions = questions

    def _give_bonus(self, points, gold):
        if self.best_attempt is not None:
            if points > self.best_attempt.points:
                points = points - self.best_attempt.points
                gold = gold - self.best_attempt.gold
                scoring.score(self.user, None, 'bonus-points', points=points)
                scoring.score(self.user, None, 'bonus-gold', gold=gold)
                add_activity(self.user, _('received {points} points and '
                	'{gold} gold bonus'' for beating his/her '
                	'highscore at quiz {quiz_name}'),
                             points=points, gold=gold, quiz_name=self.quiz.name)
        else:
            scoring.score(self.user, None, 'bonus-points', points=points)
            scoring.score(self.user, None, 'bonus-gold', gold=gold)
            add_activity(self.user, _('received {points} points'
                ' and {gold} gold bonus'
                ' for submitting quiz {quiz_name}'),
                         points=points, gold=gold, quiz_name=self.quiz.name)

    def time_left(self):
        now = datetime.now()
        return self.quiz.time_limit - (now - self.start).seconds

    def set_running(self):
        self.state = 'R'
        self.start = datetime.now()
        self.save()

    def set_played(self, results, points, gold):
        # Bonus must be given before creating a new attempt, otherwise
        # player will not be bonused in case of new highscore
        self.state = 'P'
        self._give_bonus(points, gold)
        a = QuizAttempt.objects.create(results=str(results),
                                       points=points,
                                       gold=gold)
        self.attempts.add(a)
        self.save()

    @property
    def is_running(self):
        return self.state == 'R'

    @property
    def is_not_running(self):
        return not self.state == 'R'

    @property
    def is_played(self):
        return self.state == 'P'

    def can_play_again(self):
        if self.all_attempts.count():
            return (datetime.now() - self.last_attempt.date).days\
            >= self.quiz.another_chance
        return True

    @property
    def days_until_can_replay(self):
        if self.can_play_again():
            return 0
        return self.quiz.another_chance - \
        (datetime.now() - self.last_attempt.date).days


class QuizAttempt(models.Model):
    """
     Stores information about each quiz attempt
    """
    user_to_quiz = models.ForeignKey(UserToQuiz, \
    	related_name='attempts', blank=True, null=True)
    date = models.DateTimeField(auto_now_add=True, default=True, null=True)
    results = models.TextField(blank=True, null=True)
    points = models.IntegerField(default=-1)
    gold = models.IntegerField(default=0)
