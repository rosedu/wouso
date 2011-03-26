from django.db import models
from django.contrib.auth.models import User
from core.scoring.models import History
from core.artifacts.models import Artifact

class UserProfile(models.Model):
    user = models.ForeignKey(User, unique=True, 
        related_name="%(class)s_related")
    
    # Unique differentiator for ladder
    # Do not modify it manually, use scoring.score instead
    points = models.FloatField(default=0, blank=True, null=True)
    
    artifacts = models.ManyToManyField(Artifact, blank=True)
    level_no = models.IntegerField(default=1, blank=True, null=True)
    level = models.ForeignKey(Artifact, default=Artifact.get_level_1, related_name='user_level', blank=True, null=True)
    
    @property
    def coins(self):
        return History.user_coins(self.user)
        
    def get_extension(self, cls):
        """ Search for an extension of this object, with the type cls
        Create instance if there isn't any.
        
        Using an workaround, while: http://code.djangoproject.com/ticket/7623 gets fixed.
        Also see: http://code.djangoproject.com/ticket/11618
        """
        try:
            extension = cls.objects.get(user=self.user)    
        except cls.DoesNotExist:
            extension = cls(userprofile_ptr = self)
            for f in self._meta.local_fields: 
                setattr(extension, f.name, getattr(self, f.name))
            extension.save()
                
        return extension
        
# Hack for having user and user's profile always in sync
def user_post_save(sender, instance, **kwargs):
    profile, new = UserProfile.objects.get_or_create(user=instance)
models.signals.post_save.connect(user_post_save, User)
