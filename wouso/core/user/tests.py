# coding=utf-8
from django.conf import settings
from django.contrib.auth.models import User
from django.test import TestCase
import logging
from wouso.core.magic.models import Artifact
from wouso.core.tests import WousoTest
from wouso.core.user.models import Race, PlayerGroup


class PlayerTestCase(TestCase):
    def testModifierPercents(self):
        artif = Artifact.objects.create(name='test', group=None, percents=50)
        user = User.objects.create(username='-pt-test')
        player = user.get_profile()

        player.magic.give_modifier('test', 1)
        self.assertEqual(player.magic.modifier_percents('test'), 150)

        player.magic.give_modifier('test', 1)
        self.assertEqual(player.magic.modifier_percents('test'), 200)

        artif.percents = -50
        artif.save()
        self.assertEqual(player.magic.modifier_percents('test'), 0)

        user.delete()
        artif.delete()

    def test_player_neighbours(self):
        v = []
        for i in range(0, 7):
            user = User.objects.create(username='test' + repr(i))
            player = user.get_profile()
            player.points = 10 * (10 - i)
            player.save()
            v.append(player)

        #check neighbours for first player in top
        players = v[0].get_neighbours_from_top(2)
        self.assertEqual(len(players), 5)
        for i in range(0, 5):
            self.assertEqual(players[i], v[i])

        #check neighbours for middle player in top
        players = v[3].get_neighbours_from_top(2)
        self.assertEqual(len(players), 5)
        for i in range(0, 5):
            self.assertEqual(players[i], v[i + 1])

        #check neighbours for last player in top
        players = v[6].get_neighbours_from_top(2)
        self.assertEqual(len(players), 5)
        for i in range(0, 5):
            self.assertEqual(players[i], v[i + 2])


class PlayerCacheTest(WousoTest):
    def test_race_name(self):
        p = self._get_player()
        r = Race.objects.create(name='rasa')
        self.assertEqual(p.race_name, '')
        p.race = r
        p.save()
        self.assertEqual(p.race_name, r.name)

    def test_group(self):
        p = self._get_player()
        g = PlayerGroup.objects.create(name='group')

        self.assertEqual(p.group, None)
        p.set_group(g)
        self.assertEqual(p.group, g)

    def test_cache_points(self):
        from wouso.games.challenge.models import ChallengeUser
        p = self._get_player()
        c = p.get_extension(ChallengeUser)
        p.points = 10
        p.save()
        # refetch from cache
        c = p.get_extension(ChallengeUser)
        self.assertEqual(c.points, p.points)


class PlayerCreateTest(WousoTest):
    """ Test that creating a player with diacritics in name, won't break the site
    """
    def test_unicode(self):
        settings.DISPLAY_NAME = '{first_name} {last_name}'
        try:
            User.objects.create(first_name=u'Țuțurel', last_name=u'Șănilă')
        except (UnicodeEncodeError, UnicodeDecodeError):
            self.assertTrue(False, 'Unicode names fail')

    def test_nickname_update(self):
        settings.DISPLAY_NAME = '{nickname}'
        player = self._get_player()
        self.assertEqual(unicode(player), player.user.username)

        player.nickname = 'altc3va'
        player.save()
        #self.assertEqual(unicode(player), player.nickname)
        self.assertEqual(player.full_name, player.nickname)
