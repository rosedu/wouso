"""
This file demonstrates two different styles of tests (one doctest and one
unittest). These will both pass when you run "manage.py test".

Replace these with more appropriate tests for your application.
"""
import unittest
import django.test
from django.test import TestCase
from django.test.client import Client
from wouso.interface.chat.views import *
from wouso.interface.chat.models import *
from wouso.core.user.models import User
from datetime import datetime, timedelta


class ChatTestCase(django.test.TestCase):
    def setUp(self):
        self.user, new= User.objects.get_or_create(username='_chat1')
        self.user.set_password('secret')
        self.user.save()
        self.chat_user = self.user.get_profile().get_extension(ChatUser)
        self.client = Client()
        self.client.login(username='_chat1', password='secret')


    def create_message(self, message):
        return self.client.post("/chat/m", message)

    def test_message_send_manual(self):
        room= roomexist('global')
        timeStamp = datetime.now()

        len_now = len(ChatMessage.objects.all())

        msg = ChatMessage(content='sss', author=self.chat_user, destRoom=room, timeStamp=timeStamp)
        msg.save()

        len_after = len(ChatMessage.objects.all())

        self.assertEqual(len_now, len_after - 1)

    def test_message_send_url(self):
        Room = roomexist('global')
        len_now = len(ChatMessage.objects.filter(destRoom=Room))
        resp = self.client.post('/chat/m/', {'opcode':'message','room':'global','msg':'salut'})
        len_after = len(ChatMessage.objects.filter(destRoom=Room))

        self.assertEqual(len_now, len_after - 1)

class SimpleTest(TestCase):
    def test_basic_addition(self):
        """
        Tests that 1 + 1 always equals 2.
        """
        self.failUnlessEqual(1 + 1, 2)

__test__ = {"doctest": """
Another way to test that 1 + 1 is equal to 2.

>>> 1 + 1 == 2
True
"""}

