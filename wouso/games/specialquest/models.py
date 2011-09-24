from django.db import models
from wouso.core.user.models import Player
from wouso.core.game.models import Game

# Create your models here.

class SpecialQuestTask(models.Model):
    name = models.TextField()
    text = models.TextField()
    start_date = models.DateField()
    end_date = models.DateField()

    def __unicode__(self):
            return unicode(self.name)

class SpecialQuestUser(Player):
    done_tasks = models.ManyToManyField(SpecialQuestTask, related_name="%(app_label)s_%(class)s_done")

class SpecialQuestGame(Game):
    """ Each game must extend Game """
    class Meta:
        # A Game extending core.game.models.Game should be set as proxy
        proxy = True

    def __init__(self, *args, **kwargs):
        # Set parent's fields
        self._meta.get_field('verbose_name').default = "Special Quest"
        self._meta.get_field('short_name').default = ""
        # the url field takes as value only a named url from module's urls.py
        self._meta.get_field('url').default = "specialquest_index_view"
        super(SpecialQuestGame, self).__init__(*args, **kwargs)

    @classmethod
    def get_sidebar_widget(kls, request):
        if not request.user.is_anonymous():
            from views import sidebar_widget
            return sidebar_widget(request)
        return None

    @classmethod
    def get_header_link(kls, request):
        if not request.user.is_anonymous():
            from views import header_link
            return header_link(request)
        return None
