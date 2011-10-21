from django.db import models
from django.core.urlresolvers import reverse

class StaticPage(models.Model):
    position      = models.IntegerField(primary_key=True)
    slug = models.CharField(max_length=50, blank=False)
    name = models.CharField(max_length=100, blank=False)
    title         = models.CharField(max_length=200, blank=False)
    html_contents = models.TextField()
    hidden = models.BooleanField(default=False, blank=True)

    def __unicode__(self): 
        return "%s (%s)" % (self.position, self.title)

    def html_link(self):
        return '<a href="%s">%s</a>' % (reverse('static_page', args=(self.slug,)),
                                        self.name)