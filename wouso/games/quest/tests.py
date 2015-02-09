from datetime import datetime, timedelta
from django.test import TestCase
from django.contrib.auth.models import User
from django.test import Client
from django.test.client import RequestFactory
from django.core.urlresolvers import reverse
import json
from wouso.core import scoring
from wouso.core.qpool.models import Question, Answer, Category
from models import *
from wouso.core.scoring import Coin
from wouso.core.tests import WousoTest
from wouso.core.user.models import Race
from wouso.games.quest.cpanel import quest_bonus

class QuestStatistics(WousoTest):
    def setUp(self):
        super(QuestStatistics, self).setUp()
        self.user1 = User.objects.create(username='test1')
        self.user1.set_password('test')
        self.user1.save()
        self.quest_user1 = self.user1.get_profile().get_extension(QuestUser)
        self.user2 = User.objects.create(username='test2')
        self.user2.set_password('test')
        self.user2.save()
        self.quest_user2 = self.user2.get_profile().get_extension(QuestUser)
        scoring.setup_scoring()
        category = Category.add('quest')
        question1 = Question.objects.create(text='question1', answer_type='F',
                                           category=category, active=True)
        answer1 = Answer.objects.create(text='first answer', correct=True, question=question1)
        question2 = Question.objects.create(text='question2', answer_type='F',
                                           category=category, active=True)
        answer2 = Answer.objects.create(text='second answer', correct=True, question=question2)
        start = datetime.datetime.now()
        end = datetime.datetime.now() + timedelta(days=1)
        self.quest = Quest.objects.create(start=start, end=end)
        self.quest.questions.add(question1)
        self.quest.questions.add(question2)

    def test_check_if_both_players_finished(self):
        self.quest_user1.current_quest = self.quest
        self.quest_user2.current_quest = self.quest
        self.quest.check_answer(self.quest_user1, 'first answer')
        self.quest.check_answer(self.quest_user1, 'second answer')
        self.quest.check_answer(self.quest_user2, 'first answer')
        self.quest.check_answer(self.quest_user2, 'second answer')
        self.assertTrue(self.quest_user1.finished)
        self.assertTrue(self.quest_user2.finished)
        
    def test_only_one_player_finished(self):
        self.quest_user1.current_quest = self.quest
        self.quest_user2.current_quest = self.quest
        self.quest.check_answer(self.quest_user1, 'first answer')
        self.quest.check_answer(self.quest_user1, 'second answer')
        self.assertTrue(self.quest_user1.finished)
        self.assertFalse(self.quest_user2.finished)
    
    def test_players_are_registered_if_they_start_a_quest(self):
        self.quest_user1.current_quest = self.quest
        self.quest_user2.current_quest = self.quest
        self.quest_user1.register_quest_result()
        self.quest_user2.register_quest_result()
        self.assertEqual(self.quest.players_count(), 2)
        self.assertEqual(self.quest.players_completed(), 0)

    def test_player_is_registered_to_a_previous_quest_when_he_starts_another(self):
        start = datetime.datetime.now() - timedelta(days=2)
        end = datetime.datetime.now() - timedelta(days=1)
        old_quest = Quest.objects.create(start=start, end=end)
        self.quest_user1.current_quest = old_quest

        if not self.quest_user1.current_quest.is_active:
            self.quest_user1.register_quest_result()
            self.quest_user1.current_quest = QuestGame.get_current()
        self.assertEqual(old_quest.players_count(), 1)

    def test_check_for_duplicates(self):
        self.quest_user1.current_quest = self.quest
        self.quest_user1.register_quest_result()
        self.quest_user1.register_quest_result()
        self.assertEqual(len(QuestResult.objects.all()), 1)

class QuestTestCase(WousoTest):
    def setUp(self):
        super(QuestTestCase, self).setUp()
        self.user, new = User.objects.get_or_create(username='_test')
        self.user.set_password('test')
        self.user.save()
        profile = self.user.get_profile()
        self.quest_user = profile.get_extension(QuestUser)
        scoring.setup_scoring()
 
    def tearDown(self):
        #self.user.delete()
        pass
 
    def test_check_answer(self):
        cat = Category.add('quest')
        question = Question.objects.create(text='test_q', answer_type='F',
                                           category=cat, active=True)
        answer1 = Answer.objects.create(text='test_a1', correct=True, question=question)
        answer2 = Answer.objects.create(text='test_a2', correct=True, question=question)
 
        start = datetime.datetime.now()
        end = datetime.datetime.now() + timedelta(days=1)
        quest = Quest.objects.create(start=start, end=end)
 
        quest.questions.add(question)
 
        self.assertEqual(quest.count, 1)
 
        self.quest_user.current_quest = quest
        #self.quest_user.current_level = 0
 
        quest.check_answer(self.quest_user, 'Test_a2')
 
        self.assertTrue(self.quest_user.finished)

    def test_check_bonus_for_quest(self):
        category = Category.add('quest')
        question1 = Question.objects.create(text='question1', answer_type='F',
                                           category=category, active=True)
        answer1 = Answer.objects.create(text='first answer', correct=True, question=question1)
        start = datetime.datetime.now()
        end = datetime.datetime.now() + timedelta(days=1)
        quest = Quest.objects.create(start=start, end=end)
        quest.questions.add(question1)
        self.quest_user.current_quest = quest
        quest.check_answer(self.quest_user, 'first answer')
        self.assertEqual(len(quest.top_results()), 1)

        pl = self.user.get_profile()
        pl.points = 100
        pl.save()

        admin = User.objects.create_superuser('admin', 'admin@myemail.com', 'admin')
        fact = RequestFactory()
        request = fact.get(reverse('register_results', args=[1]))
        request.user = admin
        
        #get initial points
        initial_points = pl.points

        #add quest bonus
        response = quest_bonus(request, quest.id)

        #get final points
        pl = User.objects.get(username=self.user.username)
        final_points = pl.get_profile().points

        self.assertTrue(final_points > initial_points)

class TestQuestViews(WousoTest):
    def setUp(self):
        super(TestQuestViews, self).setUp()
        self.admin = self._get_superuser()
        self.c = Client()
        self.c.login(username='admin', password='admin')
        now = datetime.datetime.now()
        Quest.objects.create(start=now-timedelta(days=2), end=now-timedelta(days=1),
                             title='Quest no. 1')
        self.q = Quest.objects.create(start=now, end=now + timedelta(days=1),
                             title='Quest no. 2')
        Quest.objects.create(start=now+timedelta(days=1), end=now + timedelta(days=2),
                             title='Quest no. 3')
        FinalQuest.objects.create(start=now, end=now+timedelta(days=1),
                                  title='Final Quest')
        scoring.setup_scoring()

    def test_quest_home_view(self):
        response = self.c.get(reverse('quest_home'))
        self.assertContains(response, 'Quest no. 1')
        self.assertContains(response, 'Quest no. 2')
        self.assertContains(response, 'Quest no. 3')
        self.assertContains(response, 'Final Quest')

    def test_history_view(self):
        questuser1 = self._get_player(1).get_extension(QuestUser)
        questuser2 = self._get_player(2).get_extension(QuestUser)
        category = Category.add('quest')
        question1 = Question.objects.create(text='question1', answer_type='F',
                                           category=category, active=True)
        answer1 = Answer.objects.create(text='first answer', correct=True, question=question1)
        self.q.questions.add(question1)
        questuser1.current_quest = self.q
        questuser2.current_quest = self.q
        self.q.check_answer(questuser1, 'first answer')
        self.q.check_answer(questuser2, 'first answer')
        
        c = Client()
        c.login(username='testuser1', password='test')
        response = c.get(reverse('quest_history'))

        # 'testuser1' appears once in overall gods section,
        # once in quest result table and once because he is logged in
        self.assertContains(response, '>testuser1<', count=3)

        # 'testuser2' appears only in overall gods and quest result table
        self.assertContains(response, '>testuser2<', count=2)

class FinalQuestTestCase(WousoTest):
    def test_final_bonus(self):
        u1 = self._get_player(1).get_extension(QuestUser)
        u2 = self._get_player(2).get_extension(QuestUser)
        r = Race.objects.create(name='rasa_buna', can_play=True)
        Formula.add('finalquest-ok', expression='points=50*({level}+1)/{level_users}')
        Formula.add('level-gold', expression='gold=0')
        Coin.add('points')
        Coin.add('gold')
        final = FinalQuest.objects.create(start=datetime.datetime.now(), end=datetime.datetime.now())
        question = Question.objects.create(text='test', answer_type='F')
        final.questions.add(question)
        question = Question.objects.create(text='test', answer_type='F')
        final.questions.add(question)

        u1.current_level = 1; u1.race = r; u1.current_quest = final
        u1.save()
        u2.current_level = 1; u2.race = r; u2.current_quest = final
        u2.save()
        final.give_level_bonus()
        u1 = QuestUser.objects.get(pk=u1.pk)
        self.assertEqual(u1.points, 50)
        u2 = QuestUser.objects.get(pk=u2.pk)
        self.assertEqual(u2.points, 50)

    def test_final_task_call_checker(self):
        from django.conf import settings
        settings.FINAL_QUEST_CHECKER_PATH = os.path.join(os.path.dirname(__file__), 'tests')

        final = FinalQuest.objects.create(start=datetime.datetime.now(), end=datetime.datetime.now(), type=TYPE_CHECKER)
        question = Question.objects.create(text='test', answer_type='F')
        final.questions.add(question)
        u1 = self._get_player(1).get_extension(QuestUser)

        self.assertFalse(final.answer_correct(0, question, u1.user.username + "wrong", u1))
        self.assertTrue(final.answer_correct(0, question, u1.user.username, u1))

    def test_final_quest_results_view(self):
        u1 = self._get_player(1).get_extension(QuestUser)
        u2 = self._get_player(2).get_extension(QuestUser)
        r = Race.objects.create(name='rasa_buna', can_play=True)
        Formula.add('finalquest-ok', expression='points=50*({level}+1)/{level_users}')
        Formula.add('level-gold', expression='gold=0')
        Coin.add('points')
        Coin.add('gold')
        final = FinalQuest.objects.create(start=datetime.datetime.now(), end=datetime.datetime.now())
        question = Question.objects.create(text='test', answer_type='F')
        final.questions.add(question)
        question = Question.objects.create(text='test', answer_type='F')
        final.questions.add(question)

        u1.current_level = 1; u1.race = r; u1.current_quest = final
        u1.save()
        u2.current_level = 1; u2.race = r; u2.current_quest = final
        u2.save()

        c = Client()
        admin = User.objects.create_superuser('admin', 'admin@myemail.com', 'admin')
        c.login(username='admin', password='admin')
        response = c.get('/cpanel/games/quest/final/results/')
        self.assertContains(response, 'testuser1')
        self.assertContains(response, 'testuser2')

# API tests
class QuestAPITestCase(WousoTest):
    def test_info(self):
        quser = self._get_player(1).get_extension(QuestUser)
        quest = Quest.objects.create(start=datetime.datetime.now(), end=datetime.datetime.now()+timedelta(days=1))
        quser.set_current(quest)

        self._client_superuser()
        response = self.client.get('/api/quest/admin/quest=%d/username=%s/' % (quest.id, quser.user.username))
        data = json.loads(response.content)

        self.assertEqual(data['user']['id'], quser.id)

    def test_level_increment(self):
        quser = self._get_player(1).get_extension(QuestUser)
        quest = Quest.objects.create(start=datetime.datetime.now(), end=datetime.datetime.now()+timedelta(days=1))
        quser.set_current(quest)
        formula = Formula.add('quest-ok')

        self._client_superuser()
        response = self.client.post('/api/quest/admin/quest=%d/username=%s/' % (quest.id, quser.user.username))
        data = json.loads(response.content)
        self.assertEqual(data['current_level'], quser.current_level + 1)
        response = self.client.post('/api/quest/admin/quest=%d/username=%s/' % (quest.id, quser.user.username))
        data = json.loads(response.content)
        self.assertEqual(data['current_level'], quser.current_level + 2)
