from wouso.core.scoring.models import Coin
from wouso.interface.messaging.models import Message, MessagingUser

__author__ = 'alex'

from piston.handler import BaseHandler
from piston.utils import rc
from django.db.models.query_utils import Q
from wouso.interface.top.models import TopUser
from wouso.core.user.templatetags.user import player_avatar
from wouso.core.game import get_games
from wouso.core.user.models import Player, SpellHistory
from wouso.core.magic.models import Spell
from wouso.core.god import God
from wouso.core import scoring
from wouso.interface.apps import get_apps

class ApiRoot(BaseHandler):
    allowed_methods = ('GET',)

    def read(self, request):
        base = 'http://%s' % request.get_host()
        fullpath = request.get_full_path()
        if '?' in fullpath:
            query = fullpath[fullpath.rindex('?'):]
        else:
            query = ''

        api = {
            'Info': '%s/api/info/%s' % (base, query),
            'Notifications': '%s/api/notifications/all/%s' % (base, query),
        }
        return api

class Search(BaseHandler):
    allowed_methods = ('GET',)

    def read(self, request, query):
        query = query.strip()
        searchresults = Player.objects.filter(Q(user__first_name__icontains=query) | Q(user__last_name__icontains=query) | Q(user__username__icontains=query))

        return [{'first_name': p.user.first_name, 'last_name': p.user.last_name, 'id': p.id} for p in searchresults]

class NotificationsHandler(BaseHandler):
    allowed_methods = ('GET',)

    def read(self, request, type):
        notifs = {}
        for app in get_apps():
            notifs[app.name()] = app.get_unread_count(request)
        for game in get_games():
            notifs[game.name()] = game.get_unread_count(request)

        all = sum(notifs.values())

        if type == 'all':
            return {'count': all, 'type': type, 'types': notifs.keys()}
        elif type in notifs.keys():
            return {'count': notifs[type], 'type': type}
        else:
            return rc.BAD_REQUEST

class InfoHandler(BaseHandler):
    allowed_methods = ('GET',)

    def read(self, request, player_id=None):
        if player_id:
            try:
                player = Player.objects.get(pk=player_id)
            except Player.DoesNotExist:
                return rc.NOT_FOUND
        else:
            try:
                player = request.user.get_profile()
            except Player.DoesNotExist:
                return rc.NOT_FOUND

        level = {
            'name': player.level.name,
            'title': player.level.title,
            'image': player.level.image,
            'id': player.level.id,
        } if player.level else {}

        group = player.groups.all()[0].name if player.groups.count() else None
        gold = player.coins['gold'] if 'gold' in player.coins.keys() else 0
        topuser = player.get_extension(TopUser)

        return {'first_name': player.user.first_name,
                'last_name': player.user.last_name,
                'email': player.user.email,
                'avatar': player_avatar(player),
                'points': player.points,
                'gold': gold,
                'race': player.race_name,
                'group': group,
                'level_no': player.level_no,
                'level': level,
                'level_progress': God.get_level_progress(player),
                'rank': topuser.position,
        }

class BazaarHandler(BaseHandler):
    allowed_methods = ('GET',)
    object_name = 'spells'

    def get_queryset(self, user=None):
        return Spell.objects.all()

    def read(self, request):
        try:
            player = request.user.get_profile()
        except Player.DoesNotExist:
            return rc.NOT_FOUND

        return {self.object_name: self.get_queryset(user=player)}

class BazaarInventoryHandler(BazaarHandler):
    def read(self, request):
        player = request.user.get_profile()

        return {'spells_available': player.spells_available,
                'spells_onme': player.spells,
                'spells_cast': player.spells_cast
        }

class BazaarBuy(BaseHandler):
    allowed_methods = ('POST',)

    def create(self, request):
        attrs = self.flatten_dict(request.POST)

        if 'spell' not in attrs.keys():
            return {'success': False, 'error': 'Spell not provided'}

        try:
            spell = int(attrs['spell'])
            spell = Spell.objects.get(pk=spell)
        except (ValueError, Spell.DoesNotExist):
            return {'success': False, 'error': 'No such spell'}

        # TODO refactor
        player = request.user.get_profile()
        if spell.price > player.coins.get('gold', 0):
            return {'success': False, 'error': 'Insufficient gold'}
        else:
            player.add_spell(spell)
            scoring.score(player, None, 'buy-spell', external_id=spell.id,
                price=spell.price)
            SpellHistory.bought(player, spell)
            return {'success': True}

class BazaarExchange(BaseHandler):
    allowed_methods = ('POST',)

    def create(self, request, coin, tocoin):
        try:
            coin = Coin.objects.get(id=coin)
            tocoin = Coin.objects.get(id=tocoin)
        except Coin.DoesNotExist:
            return {'success': False, 'error': 'Invalid coin'}

        attrs = self.flatten_dict(request.POST)
        if 'amount' not in attrs.keys():
            return {'success': False, 'error': 'Amount not provided'}

        player = request.user.get_profile()
        try:
            amount = int(attrs['amount'])
            assert amount > 0
        except (ValueError, AssertionError):
            return {'success': False, 'error': 'Invalid Amount'}

        if player.coins[coin.id] < amount:
            return {'success': False, 'error': 'Insufficient amount'}

        # TODO: change me
        if coin.id == 'points':
            scoring.score(player, None, 'points-gold-rate', points=amount)
        elif coin.id == 'gold':
            scoring.score(player, None, 'gold-points-rate', gold=amount)

        return {'success': True, 'coins': player.coins}

class Messages(BaseHandler):
    LIMIT = 100

    def read(self, request, type='all'):
        player = request.user.get_profile()
        msguser = player.get_extension(MessagingUser)
        if type == 'all':
            return Message.objects.filter(Q(sender=msguser)|Q(receiver=msguser))[:self.LIMIT]
        elif type == 'sent':
            return Message.objects.filter(sender=msguser)[:self.LIMIT]
        elif type == 'recv':
            return Message.objects.filter(receiver=msguser)[:self.LIMIT]

class MessagesSender(BaseHandler):
    allowed_methods = ('POST',)

    def create(self, request):
        attrs = self.flatten_dict(request.POST)
        sender = request.user.get_profile()

        if 'receiver' not in attrs.keys():
            return {'success': False, 'error': 'Missing receiver'}

        try:
            if attrs['receiver'].isdigit():
                receiver = Player.objects.get(pk=attrs['receiver'])
            else:
                receiver = Player.objects.get(user__username=attrs['receiver'])
        except Player.DoesNotExist:
            return {'success': False, 'error': 'Invalid receiver'}

        if 'text' not in attrs.keys():
            return {'success': False, 'error': 'Missing text'}

        if 'subject' not in attrs.keys():
            attrs['subject'] = ''

        try:
            reply_to = Message.objects.get(pk=attrs['reply_to'])
        except (KeyError, Message.DoesNotExist):
            reply_to = None

        Message.send(sender, receiver, attrs['subject'], attrs['text'], reply_to=reply_to)

        return {'success': True}