"""
This file demonstrates two different styles of tests (one doctest and one
unittest). These will both pass when you run "manage.py test".

Replace these with more appropriate tests for your application.
"""
import unittest
import json
from datetime import datetime
from django.test.client import Client
from wouso.core.tests import WousoTest
from wouso.interface.chat.views import roomexist
from wouso.interface.chat.models import ChatUser, ChatRoom, ChatMessage
from wouso.core.user.models import User

class ChatTestCase(WousoTest):
    """
        After setUp method is passed, you are login with "_chat1" account
        Author for all next messages will be "_chat1", the login user
        There exist 3 types of query for /chat/m url:
            - message, that send to a specific room a specific message
            - keepAlive, that make the user a global user
            - getRoom, that create or giving an existing room for 2 persons.
    """
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
        self.time_stamp = datetime.now()
        self.client = Client()
        self.client.login(username='_chat2', password='secret')
        self.client.post('/chat/chat_m/', {'opcode':'keepAlive', 'time':self.time_stamp})
        self.client.logout()

        self.client.login(username='_chat1', password='secret')
        self.client.post('/chat/chat_m/', {'opcode':'keepAlive', 'time':self.time_stamp})
        super(ChatTestCase, self).setUp()



    def test_message_send_manual(self):
        room= roomexist('global')
        time_stamp = datetime.now()

        len_now = len(ChatMessage.objects.all())
        msg = ChatMessage(content='sss', author=self.chat_user, dest_room=room, time_stamp=time_stamp, mess_type = "normal", comand = "normal")
        msg.save()
        len_after = len(ChatMessage.objects.all())

        self.assertEqual(len_now, len_after - 1)

    def test_message_send_url(self):
        len_now = len(ChatMessage.objects.all())
        self.client.post("/chat/chat_m/", {'opcode':'message','room': 'global','msg': 'salut', 'time': self.time_stamp})
        len_after = len(ChatMessage.objects.all())

        last_mess = ChatMessage.objects.all()
        self.assertEqual(len_now, len_after - 1)
        self.assertEqual(last_mess[0].content, 'salut')


    def test_message_send_url_private(self):
        resp = self.client.post('/chat/chat_m/', {'opcode':'getRoom', 'from':self.user.id, 'to':self.user1.id, 'time':self.time_stamp})
        room = json.loads(resp.content)
        room_name = str(self.user.id) + '-' + str(self.user1.id)

        self.client.post("/chat/chat_m/", {'opcode':'message','room': room['name'],'msg': 'Buna', 'time':self.time_stamp})
        self.client.post("/chat/chat_m/", {'opcode':'message','room': 'global'    ,'msg': 'Salut', 'time':self.time_stamp})

        self.assertEqual(room['name'], room_name)
        self.assertEqual(len(ChatMessage.objects.filter(dest_room__name=room['name'], dest_room__participants=self.user)), 1)
        self.assertEqual(len(ChatMessage.objects.filter(dest_room__name=room['name'], dest_room__participants=self.user1)), 1)
        self.assertEqual(len(ChatMessage.objects.filter(dest_room__name=room['name'], dest_room__participants=self.user2)), 0)
        self.assertEqual(len(ChatMessage.objects.filter(dest_room__name='global')), 1)



    def test_message_send_more_message(self):

        for i in range(10):
            message_content = 'salut' + str(i)
            self.client.post("/chat/chat_m/", {'opcode':'message','room': 'global','msg': message_content, 'time':self.time_stamp})

        last_mess = ChatMessage.objects.filter(dest_room__name='global')
        for i in range(10):
            self.assertEqual(last_mess[i].content, 'salut' + str(i))


        self.assertEqual(len(ChatMessage.objects.filter(dest_room__name='global', dest_room__participants=self.user)), 10)

    def test_combine_messages(self):
        self.test_message_send_more_message()

        resp = self.client.post('/chat/chat_m/', {'opcode':'getRoom', 'from': self.user.id, 'to':self.user1.id, 'time':self.time_stamp})
        room1 = json.loads(resp.content)

        resp = self.client.post('/chat/chat_m/', {'opcode':'getRoom', 'from': self.user.id, 'to':self.user2.id, 'time':self.time_stamp})
        room2 = json.loads(resp.content)


        for i in range(10):
            self.client.post("/chat/chat_m/", {'opcode':'message','room': room1['name'],'msg': 'Buna' + str(i), 'time':self.time_stamp})
            if i % 2 == 0: self.client.post("/chat/chat_m/", {'opcode':'message','room': room2['name'],'msg': 'Buna' + str(i),'time':self.time_stamp})

        self.assertEqual(len(ChatMessage.objects.filter(dest_room__participants= self.user)),25) #all message
        self.assertEqual(len(ChatMessage.objects.filter(dest_room__participants= self.user).filter(dest_room__participants= self.user1)), 20)
        self.assertEqual(len(ChatMessage.objects.filter(dest_room__participants= self.user).filter(dest_room__participants= self.user2)), 5)
        self.assertEqual(len(ChatMessage.objects.filter(dest_room__participants= self.user1)), 20)
        self.assertEqual(len(ChatMessage.objects.filter(dest_room__name=room1['name'])), 10)
        self.assertEqual(len(ChatMessage.objects.filter(dest_room__name=room2['name'])), 5)
        self.assertEqual(len(ChatMessage.objects.filter(dest_room__participants= self.user1).filter(dest_room__participants= self.user2)), 0)


    def test_private_log_url(self):
        resp = self.client.post('/chat/chat_m/', {'opcode':'getRoom', 'from':self.user.id, 'to':self.user1.id, 'time':self.time_stamp})
        room = json.loads(resp.content)

        for i in range(10):
            self.client.post("/chat/chat_m/", {'opcode':'message','room': room['name'],'msg': 'Buna' + str(i), 'time':self.time_stamp})

        resp = self.client.post('/chat/privateLog/', {'room':room['name'], 'number':'0'})
        private_log = json.loads(resp.content)
        for i in range(10):
            msg = 'Buna' + str(i)
            self.assertEqual(private_log['count'], 10)
            self.assertEqual(private_log['msgs'][i]['text'], msg)


    @unittest.expectedFailure
    def test_global_log(self):

        for i in range(10):
            message_content = 'Hello' + str(i)
            self.client.post("/chat/chat_m/", {'opcode':'message','room': 'global','msg': message_content, 'time':self.time_stamp})

        log = self.client.get("/chat/log/")
        room = roomexist('global')
        all_message = ChatMessage.objects.filter(dest_room=room)
        all_message = all_message[len(all_message)-50:] if len(all_message) > 50 else all_message
        self.assertEqual(len(log.content), len(all_message))
