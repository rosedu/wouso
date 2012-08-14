from django.contrib import admin
from models import Device

class DeviceAdmin(admin.ModelAdmin):
    list_display = ('__unicode__', 'player', 'registered')

admin.site.register(Device, DeviceAdmin)