__author__ = 'alex'

from django.contrib import admin
from django.contrib.admin.sites import AlreadyRegistered
from piston.models import Consumer, Nonce, Token

try:
    admin.site.register(Consumer)
    admin.site.register(Nonce)
    admin.site.register(Token)
except AlreadyRegistered:
    pass