from django.db import models
from wouso.core.common import App


class FileCategory(models.Model):
    name = models.CharField(max_length=100, unique=True)

    @property
    def files(self):
        return self.file_set.all()

    def __unicode__(self):
        return self.name


class File(models.Model, App):
    name = models.CharField(max_length=100, unique=True)
    file = models.FileField(upload_to='storage')
    category = models.ForeignKey(FileCategory)
    type = models.CharField(max_length=10)

    def __unicode__(self):
        return self.name
