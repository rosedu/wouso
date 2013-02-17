from django.contrib.auth.models import User
from django.test import TestCase
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
        for i in range(0,7):
            user = User.objects.create(username='test' + repr(i))
            player = user.get_profile()
            player.points = 10*(10-i)
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
        for i in range(0,5):
            self.assertEqual(players[i],v[i+1])

        #check neighbours for last player in top
        players = v[6].get_neighbours_from_top(2)
        self.assertEqual(len(players), 5)
        for i in range(0,5):
            self.assertEqual(players[i], v[i+2])


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