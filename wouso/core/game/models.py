from django.db import models

class Game(models.Model):
    name = models.CharField(max_length=100, primary_key=True)
    
    @classmethod
    def get_instance(kls):
        instance, new = kls.objects.get_or_create(name=kls.__name__)
        instance.game = Game.objects.get(name=kls.__name__)
        return instance
    
    @classmethod
    def get_formulas(kls):
        """ Returns a list of formulas used by the game """
        return []
        
    @classmethod
    def get_coins(kls):
        """ Returns a list of game-specific coins """
        return []
    
    @classmethod
    def get_sidebar_widget(kls, request):
        """ Return the sidebar widget, for current HttpRequest request.
        This is called in interface.context_processors.sidebar """
        return None
