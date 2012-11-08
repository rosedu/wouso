from django.contrib import admin
from models import MessagingUser, Message

class MessageAdmin(admin.ModelAdmin):
    list_filter = ('read', 'sender', 'receiver')
    list_display = ('__unicode__', 'subject', 'text', 'timestamp')

admin.site.register(MessagingUser)
admin.site.register(Message, MessageAdmin)
