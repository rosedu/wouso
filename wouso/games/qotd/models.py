from datetime import datetime, timedelta
from django.db import models
from core.user.models import UserProfile
from core.game.models import Game
from core import scoring
from core.scoring.models import Formula

# Qotd will use models (question) from qpool
# Please implement wouso.core.qpool

class QotdUser(UserProfile):
    """ Extension of the User object, customized for qotd """
    last_answered = models.DateTimeField(null=True, blank=True, default=None)
    last_answer = models.IntegerField(default=0, blank=True)
    def set_answered(self, correct):
        if not self.has_answered:
            self.last_answer = correct
            self.last_answered = datetime.now()
            self.save()
        
    def reset_answered(self):
        self.last_answered = None
        self.save()
        
    @property
    def has_answered(self):
        """ Check if last_answered was today """
        if self.last_answered is None:
            return False
        else:
            return (datetime.now() - self.last_answered) < timedelta (days = 1)
    
class QotdGame(Game):
    """ Each game must extend Game """
    class Meta:
        # The verbose_name is used in fine printing
        verbose_name = "Question of the Day"
        # A Game extending core.game.models.Game should be set as proxy
        proxy = True
    
    @staticmethod
    def get_for_today():
        """ Return a Question object selected for Today """
        class Question: pass
        class Answer: pass
        q = Question()
        q.text = 'How many'
        q.answers = []
        for i in range(4):
            a = Answer()
            a.id, a.text, a.correct = i, str(i), True if i == 2 else False
            q.answers.append(a)
        return q
        
    @staticmethod
    def answered(user, question, choice):
        correct = False
        for a in question.answers:
            if a.id == choice and a.correct:
                correct = True
                break
        
        user.set_answered(choice)
        
        if correct:
            scoring.score(user, QotdGame, 'qotd-ok')
    
    @classmethod
    def get_formulas(kls):
        """ Returns a list of formulas used by qotd """
        fs = []
        qotd_game = kls.get_instance()
        fs.append(Formula(id='qotd-ok', formula='points=3', 
            owner=qotd_game.game, 
            description='Points earned on a correct answer')
        )
        return fs
    
    @classmethod
    def get_sidebar_widget(kls, request):
        if not request.user.is_anonymous():
            from views import sidebar_widget
            return sidebar_widget(request)
        return None
