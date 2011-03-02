from django.db import models
from django.contrib.auth.models import User

class UserProfile(models.Model):
    user = models.ForeignKey(User, unique=True, 
        related_name="%(class)s_related")
    
    def get_extension(self, cls):
        """ Search for an extension of this object, with the type cls
        Creat instance if there isn't any
        """
        profile, new = cls.objects.get_or_create(user=self.user)    
        return profile
        
# Hack for having user and user's profile always in sync
def user_post_save(sender, instance, **kwargs):
    profile, new = UserProfile.objects.get_or_create(user=instance)
models.signals.post_save.connect(user_post_save, User)
