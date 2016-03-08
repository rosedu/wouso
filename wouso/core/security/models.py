from datetime import datetime
from django.db import models
from wouso.core.user.models import Player


class Report(models.Model):
    STATUS = (
        ("R", "Reported"),
        ("I", "Investigating"),
        ("S", "Resolved"),
        ("E", "Invalid"),
    )

    user_from = models.ForeignKey(Player, related_name="user_reporting")
    user_to   = models.ForeignKey(Player, related_name="user_reported")
    dibs      = models.ForeignKey(Player, related_name="dibs", null=True, blank=True)
    timestamp = models.DateTimeField()
    status    = models.CharField(max_length=1, choices=STATUS, default='R')
    text      = models.CharField(max_length=250)
    extra     = models.CharField(max_length=250, blank=True)

    def set_dibs(self, user_dibs):
        self.dibs = user_dibs.get_extension(Player)
        self.save()

    def set_status(self, status="R"):
        self.status = status
        self.save()

    def set_extra(self, text=""):
        self.extra = text
        self.save()

    def __unicode__(self):
        return self.user_from.__unicode__() + " on " + self.user_to.__unicode__() + ":" + self.text[:20]


def add_report(user_from, user_to, text):
    report = Report(user_from=user_from.get_profile().get_extension(Player),
                    user_to=user_to.get_profile().get_extension(Player),
                    text=text, timestamp=datetime.now())
    report.save()
