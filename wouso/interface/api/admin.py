__author__ = 'alex'

from django.contrib import admin
from piston.models import Consumer, Nonce, Token

admin.site.register(Consumer)
admin.site.register(Nonce)
admin.site.register(Token)