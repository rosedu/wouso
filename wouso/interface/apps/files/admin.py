from django.contrib import admin
from interface.apps.files.models import File, FileCategory


admin.site.register(File)
admin.site.register(FileCategory)

