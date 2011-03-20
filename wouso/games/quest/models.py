import logging
import datetime
from django.db import models
from core.user.models import UserProfile
from core.game.models import Game
from core.qpool.models import Question
from core.qpool import get_questions_with_tags

# Quest will use QPool questions tagged 'quest'

class QuestUser(UserProfile):
    current_quest = models.ForeignKey('Quest', null=True, blank=True, default=None)
    current_level = models.IntegerField(default=0, blank=True)
    finished = models.BooleanField(default=False, blank=True)
    
    @property
    def current_question(self):
        if not self.current_quest:
            return None
        try:
            return self.current_quest.questions.all()[self.current_level]
        except IndexError:
            return None
            
    def finish_quest(self):
        if not self.finished:
            # TODO: insert into questresult
            self.finished = True
            self.save()
    
    def set_current(self, quest):
        self.current_quest = quest
        self.current_level = 0
        self.finished = False
        self.save()

class QuestResult(models.Model):
    user = models.ForeignKey('QuestUser')
    quest = models.ForeignKey('Quest')
    level = models.IntegerField(default=0)
    
class Quest(models.Model):
    start = models.DateTimeField()
    end = models.DateTimeField()
    title = models.CharField(default="", max_length=100)
    max_levels = models.IntegerField(default=0)
    questions = models.ManyToManyField(Question)
    
    @property
    def levels(self):
        return self.questions.count()
    
    @property
    def elapsed(self):
        return datetime.datetime.now() - self.start
        
    @property
    def remaining(self):
        return self.end - datetime.datetime.now()
    
    def check_answer(self, user, answer):
        if user.current_quest != self:
            user.finish_quest()
            user.set_current(self)
            return False
        try:
            question = self.questions.all()[user.current_level]
        except IndexError:
            logging.error("No such question")
            return False
        
        if not user.current_level == self.levels and \
                answer == question.answers.all()[0].text:
            user.current_level += 1
            #scoring.score()
            if user.current_level == self.levels:
                user.finish_quest()
            user.save()
            return True
        return False
            
    def __unicode__(self):
        return "%s - %s" % (self.start, self.end)
    
class QuestGame(Game):
    """ Each game must extend Game """
    class Meta:
        verbose_name = "Weekly Quest"
        proxy = True
    
    @staticmethod
    def get_current():
        try:
            return Quest.objects.get(start__lte=datetime.datetime.now(),
                                end__gte=datetime.datetime.now())
        except Quest.DoesNotExist:
            return None
    
    @classmethod
    def get_formulas(kls):
        """ Returns a list of formulas used by qotd """
        fs = []
        quest_game = kls.get_instance()
        fs.append(Formula(id='quest-ok', formula='points={level}', 
            owner=quest_game.game, 
            description='Points earned when finishing a level. Arguments: level.')
        )
        return fs
