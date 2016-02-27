import datetime
from django.db import models
from django.core.urlresolvers import reverse, NoReverseMatch
from wouso.core.user.models import Player ## this needs to be fixed to wouso.core.user.models


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
        try:
            return '<a href="%s" id="page-%s">%s</a>' % (reverse('static_page', args=(self.slug,)),
                                        self.slug, self.name)
        except NoReverseMatch:
            return ''

    @classmethod
    def get_links(cls):
        result = [sp.html_link() for sp in cls.objects.filter(hidden=False).order_by('position')]
        return result


class NewsItem(models.Model):
    title = models.CharField(max_length=100)
    text = models.TextField(max_length=500)
    author = models.ForeignKey(Player)
    date_pub = models.DateField(default=datetime.date.today)

    def __unicode__(self):
        return unicode(self.title)
