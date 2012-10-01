from django.db import models

class SecurityConfig(models.Model):
    """Class that allows enabling / disabling of security rules"""

    APP_ON_CHOICES = (('chall-won', 'Challenge Won'), ('login', 'Login'))

    id = models.CharField(max_length=100, primary_key=True)
    applies_on = models.CharField(max_length=100, choices=APP_ON_CHOICES)
    description = models.CharField(max_length=100)
    penalty_value = models.IntegerField(default=5, blank=False)
    enabled = models.BooleanField(default=True, blank=False)

    def __unicode__(self):
        return self.id
