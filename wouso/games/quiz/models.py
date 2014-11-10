from datetime import datetime

from django.db import models

from wouso.core.user.models import Player
from wouso.core.game.models import Game
from wouso.core.qpool import register_category
from wouso.core.qpool.models import Question


class QuizException(Exception):
    pass


class Quiz(models.Model):
    CHOICES = {
        ('A', 'ACTIVE'),
        ('I', 'INACTIVE'),  # Active in future
        ('E', 'EXPIRED')
    }
    name = models.CharField(max_length=100)
    number_of_questions = models.IntegerField(default=5)
    time_limit = models.IntegerField(default=300)

    points_reward = models.IntegerField(default=100)
    gold_reward = models.IntegerField(default=30)

    questions = models.ManyToManyField(Question)

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

    def calculate_points(self, responses):
        """ Response contains a dict with question id and checked answers ids.
        Example:
            {1 : [14,], ...}, - has answered answer with id 14 at the question with id 1
        """
        points = 0
        results = {}
        for r, v in responses.iteritems():
            checked, missed, wrong = 0, 0, 0
            q = Question.objects.get(id=r)
            correct_count = len([a for a in q.answers if a.correct])
            wrong_count = len([a for a in q.answers if not a.correct])
            for a in q.answers.all():
                if a.correct:
                    if a.id in v:
                        checked += 1
                    else:
                        missed += 1
                elif a.id in v:
                    wrong += 1
            if correct_count == 0:
                qpoints = 1 if (len(v) == 0) else 0
            elif wrong_count == 0:
                qpoints = 1 if (len(v) == q.answers.count()) else 0
            else:
                # qpoints = checked - wrong
                qpoints = checked
            qpoints = qpoints if qpoints > 0 else 0
            points += qpoints
            results[r] = (checked, correct_count)

        points = int(float(points) / len(q.answers) * self.max_points)

        return {'points': points, 'results': results}


class QuizGame(Game):
    """ Each game must extend Game"""
    class Meta:
        proxy = True

    QPOOL_CATEGORY = 'quiz'

    def __init__(self, *args, **kwargs):
        self._meta.get_field('verbose_name').default = "Quiz"
        self._meta.get_field('short_name').default = ""
        self._meta.get_field('url').default = "quiz_index_view"
        super(QuizGame, self).__init__(*args, **kwargs)


register_category(QuizGame.QPOOL_CATEGORY, QuizGame)


class QuizUser(Player):
    """ Extension of the User object, customized for quiz """
    quizzes = models.ManyToManyField(Quiz, through='UserToQuiz')

    @property
    def active_quizzes(self):
        through = UserToQuiz.objects.filter(user=self)
        active_quizzes = [t for t in through if t.quiz.is_active()]
        return active_quizzes

    @property
    def expired_quizzes(self):
        through = UserToQuiz.objects.filter(user=self)
        expired_quizzes = [t for t in through if t.quiz.is_expired()]
        return expired_quizzes

    @property
    def all_quizzes(self):
        through = UserToQuiz.objects.filter(user=self)
        return through


Player.register_extension('quiz', QuizUser)


class UserToQuiz(models.Model):
    CHOICES = {
        ('P', 'PLAYED'),
        ('R', 'RUNNING'),
        ('N', 'NOT RUNNING')
    }

    user = models.ForeignKey(QuizUser)
    quiz = models.ForeignKey(Quiz)
    state = models.CharField(max_length=1, choices=CHOICES, default='N')
    attempts = models.ManyToManyField('QuizAttempt')

    start = models.DateTimeField(blank=True, null=True)

    def _give_bonus(self, points):
        """TODO"""
        pass

    def time_left(self):
        now = datetime.now()
        return self.quiz.time_limit - (now - self.start).seconds

    def set_running(self):
        self.state = 'R'
        self.start = datetime.now()
        self.save()

    def set_played(self, points):
        self.state = 'P'
        self.start = None
        self.attempts.create(points=points, date=datetime.now())
        self._give_bonus(points)
        self.save()

    def is_running(self):
        return self.state == 'R'

    def is_not_running(self):
        return self.state == 'N'

    def is_played(self):
        return self.state == 'P'

    def can_play_again(self):
        if self.attempts.all().count():
            last_attempt = self.attempts.all().reverse()[0].date
            return (datetime.now() - last_attempt).days >= self.quiz.another_chance

        return True


class QuizAttempt(models.Model):
    """
     Stores information about each quiz attempt
    """
    points = models.IntegerField(default=-1)
    date = models.DateTimeField(blank=True, null=True)
