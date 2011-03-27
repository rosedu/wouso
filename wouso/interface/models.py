from django.db import models

class StaticPage(models.Model):
    position      = models.IntegerField(primary_key=True)
    title         = models.CharField(max_length=50, blank=False)
    html_contents = models.TextField()

    def __unicode__(self): 
        return "%s (%s)" % (self.position, self.title)

