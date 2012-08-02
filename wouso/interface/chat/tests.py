"""
This file demonstrates two different styles of tests (one doctest and one
unittest). These will both pass when you run "manage.py test".

Replace these with more appropriate tests for your application.
"""
import django.test
from django.test.client import Client
from wouso.interface.chat.views import *
from wouso.interface.chat.models import *
from wouso.core.user.models import User
from datetime import datetime
import json

class ChatTestCase(django.test.TestCase):
    def setUp(self):
        self.user, new= User.objects.get_or_create(username='_chat1')
        self.user.set_password('secret')
        self.user.save()

        self.user1, new= User.objects.get_or_create(username='_chat2')
        self.user1.set_password('secret')
        self.user1.save()

        self.user2, new= User.objects.get_or_create(username='_chat3')
        self.user2.set_password('secret')
        self.user2.save()


        self.chat_user = self.user.get_profile().get_extension(ChatUser)

        self.client = Client()
        self.client.login(username='_chat1', password='secret')

    def test_message_send_manual(self):
        room= roomexist('global')
        timeStamp = datetime.now()

        len_now = len(ChatMessage.objects.all())

        msg = ChatMessage(content='sss', author=self.chat_user, destRoom=room, timeStamp=timeStamp)
        msg.save()

        len_after = len(ChatMessage.objects.all())

        self.assertEqual(len_now, len_after - 1)


    def create_message(self, input_msg, room):
        data = {'opcode':'message','room': room,'msg': input_msg}
        return self.client.post('/chat/m/', data)


    def create_getRoom(self, myID, sendID):
        data = {'opcode':'getRoom', 'from':myID, 'to':sendID}
        return self.client.post('/chat/m/', data)


    def create_keepAlive(self):
        return self.client.post('/chat/m/', {'opcode':'keepAlive'})

    def test_message_send_url(self):
        len_now = len(ChatMessage.objects.all())
        message_content = 'salut'
        self.create_message(message_content, 'global')
        len_after = len(ChatMessage.objects.all())

        last_mess = ChatMessage.objects.all()
        self.assertEqual(len_now, len_after - 1)
        self.assertEqual(last_mess[0].content, message_content)


    def test_message_send_url_private(self):
        resp = self.create_getRoom(self.user.id, self.user1.id)
        room = json.loads(resp.content)
        room_name = str(self.user.id) + '-' + str(self.user1.id)

        self.create_keepAlive()
        self.create_message("Buna", room['name'])
        self.create_message("Salut", 'global')

        self.assertEqual(room['name'], room_name)
        self.assertEqual(len(ChatMessage.objects.filter(destRoom__name=room['name'], destRoom__participants=self.user)), 1)
        self.assertEqual(len(ChatMessage.objects.filter(destRoom__name=room['name'], destRoom__participants=self.user1)), 1)
        self.assertEqual(len(ChatMessage.objects.filter(destRoom__name=room['name'], destRoom__participants=self.user2)), 0)
        self.assertEqual(len(ChatMessage.objects.filter(destRoom__name='global', destRoom__participants=self.user)), 1)



    def test_message_send_more_message(self):

        self.create_keepAlive()

        for i in range(10):
            message_content = 'salut' + str(i)
            self.create_message(message_content, 'global')

        last_mess = ChatMessage.objects.all()
        for i in range(10):
            self.assertEqual(last_mess[i].content, 'salut' + str(i))


        self.assertEqual(len(ChatMessage.objects.filter(destRoom__name='global', destRoom__participants=self.user)), 10)
