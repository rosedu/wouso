from datetime import datetime, timedelta
from django.shortcuts import get_object_or_404
from django.template.defaultfilters import slugify
from django.utils.html import strip_tags
from piston.handler import BaseHandler
from piston.utils import rc

from django.db.models.query_utils import Q
from django.db.models.aggregates import Sum

from wouso.core.config.models import Setting
from wouso.core.qpool.models import Category
from wouso.core.scoring.models import Coin
from wouso.core.user.templatetags.user import player_avatar
from wouso.core.game import get_games
from wouso.core.user.models import Player, Race, PlayerGroup
from wouso.core.magic.models import Spell, SpellHistory
from wouso.core.god import God
from wouso.core import scoring
from wouso.interface import get_custom_theme
from wouso.interface.apps import get_apps
from wouso.interface.activity.models import Activity
from wouso.interface.api.c2dm.models import register_device
from wouso.interface.apps.messaging.models import Message, MessagingUser
from wouso.interface.top.models import TopUser, GroupHistory
from wouso.interface.apps.lesson.models import LessonCategory, LessonTag

from . import API_VERSION

def get_fullpath(request):
    base = 'http://%s' % request.get_host()
    fullpath = request.get_full_path()
    if '?' in fullpath:
        query = fullpath[fullpath.rindex('?'):]
    else:
        query = ''
    return base + fullpath, query

class ApiRoot(BaseHandler):
    allowed_methods = ('GET',)

    def read(self, request):
        api = {
            'api_version': API_VERSION,
            'title': Setting.get('title').get_value(),
            'authenticated': request.user.is_authenticated()
        }
        return api

class Search(BaseHandler):
    allowed_methods = ('GET',)

    def read(self, request, query):
        query = query.strip()
        searchresults = Player.objects.filter(Q(user__first_name__icontains=query) | Q(user__last_name__icontains=query) | Q(user__username__icontains=query))

        return [{'first_name': p.user.first_name, 'last_name': p.user.last_name, 'id': p.id} for p in searchresults]


class OnlineUsers(BaseHandler):
    allowed_methods = ('GET',)

    def read(self, request, type=None):
        oldest = datetime.now() - timedelta(minutes = 10)
        online_last10 = Player.objects.filter(last_seen__gte=oldest).order_by('-last_seen')

        if type == 'list':
            return [u.nickname for u in online_last10]
            # default, more info
        return [{'nickname': u.nickname, 'first_name': u.user.first_name, 'last_name': u.user.last_name,
                 'id': u.id, 'last_seen': u.last_seen} for u in online_last10]


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

class NotificationsRegister(BaseHandler):
    allowed_methods = ('POST',)

    def create(self, request):
        attrs = self.flatten_dict(request.POST)

        if 'registration_id' not in attrs.keys():
            return {'success': False, 'error': 'No registration_id provided'}

        player = request.user.get_profile()

        register_device(player, attrs['registration_id'])
        return {'success': True}

class NotificationsDevices(BaseHandler):
    allowed_methods = ('GET',)

    def read(self, request):
        player = request.user.get_profile()
        return [dict(registration_id=d.registration_id) for d in player.device_set.all()]

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

        group = player.group
        gold = player.coins['gold'] if 'gold' in player.coins.keys() else 0
        topuser = player.get_extension(TopUser)

        return {'username': player.user.username,
                'nickname': player.nickname,
                'first_name': player.user.first_name,
                'last_name': player.user.last_name,
                'email': player.user.email,
                'avatar': player_avatar(player),
                'points': player.points,
                'gold': gold,
                'race': player.race_name,
                'race_slug': player.race.name.lower() if player.race and player.race.name else '',
                'race_id': player.race.id if player.race else 0,
                'group': group,
                'level_no': player.level_no,
                'level': level,
                'level_progress': God.get_level_progress(player),
                'rank': topuser.position,
                }


class ChangeNickname(BaseHandler):
    allowed_methods = ('GET', 'POST',)

    def read(self, request):
        return {'nickname': request.user.get_profile().nickname}

    def create(self, request):
        """
        Attempt to change the nickname
        """
        player = request.user.get_profile()
        nickname = request.POST.get('nickname')
        if not nickname:
            return {'success': False, 'error': 'Nickname not provided'}
        if nickname == player.nickname:
            return {'success': False, 'error': 'Nickname is the same'}
        if Player.objects.exclude(id=player.id).filter(nickname=nickname).count() > 0:
            return {'success': False, 'error': 'Nickname in use'}
        player.nickname = slugify(strip_tags(nickname))
        player.save()
        return {'success': True}


class ChangeTheme(ChangeNickname):
    def read(self, request):
        from wouso.interface import get_custom_theme
        from wouso.utils import get_themes
        return {'theme': get_custom_theme(request.user.get_profile()), 'themes': get_themes()}

    def create(self, request):
        from wouso.interface import set_custom_theme
        player = request.user.get_profile()
        theme = request.POST.get('theme')
        if not theme:
            return {'success': False, 'error': 'Theme not provided'}
        if set_custom_theme(player, theme):
            return {'success': True}
        else:
            return {'success': False, 'error': 'Theme does not exist'}


class BazaarHandler(BaseHandler):
    allowed_methods = ('GET',)
    object_name = 'spells'
    fields = ('name', 'title', 'description', 'available', 'due_days', 'type', 'mass', 'level_required', 'image_url',
              'price', 'id')

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

        spells_available = [{'spell_id': s.spell.id, 'spell_name': s.spell.name, 'spell_title': s.spell.title,
                             'image_url': s.spell.image_url, 'amount': s.amount, 'due_days': s.spell.due_days} for s in player.magic.spells_available]
        spells_onme = [{'spell_id': s.spell.id, 'spell_name': s.spell.name, 'spell_title': s.spell.title, 'due': s.due,
                        'source': unicode(s.source), 'source_id': s.source.id, 'image_url': s.spell.image_url} for s in player.magic.spells]
        spells_cast = [{'spell_id': s.spell.id, 'spell_name': s.spell.name, 'spell_title': s.spell.title, 'due': s.due,
                        'player_id': s.player.id, 'player': unicode(s.player), 'image_url': s.spell.image_url} for s in player.magic.spells_cast]
        return {'spells_available': spells_available,
                'spells_onme': spells_onme,
                'spells_cast': spells_cast
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
            player.magic.add_spell(spell)
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

    def to_dict(self, m):
        """
        :param m: Message instance
        :return: dictionary
        """
        return {'id': m.id, 'date': m.timestamp,
                'from': unicode(m.sender), 'from_id': m.sender_id,
                'to': unicode(m.receiver), 'to_id': m.receiver_id,
                'text': m.text,
                'subject': m.subject, 'reply_to': m.reply_to.id if m.reply_to else None,
                'read': m.read
        }

    def read(self, request, type='all'):
        player = request.user.get_profile()
        msguser = player.get_extension(MessagingUser)
        if type == 'all':
            qs = Message.objects.filter(Q(sender=msguser)|Q(receiver=msguser)).exclude(archived=True)[:self.LIMIT]
        elif type == 'sent':
            qs = Message.objects.filter(sender=msguser)[:self.LIMIT]
        elif type == 'recv':
            qs = Message.objects.filter(receiver=msguser).exclude(archived=True)[:self.LIMIT]
        else:
            return []
        return [self.to_dict(m) for m in qs]

class MessagesSender(BaseHandler):
    allowed_methods = ('POST',)

    def create(self, request):
        attrs = self.flatten_dict(request.POST)
        sender = request.user.get_profile()

        try:
            reply_to = Message.objects.get(pk=attrs['reply_to'])
            receiver = reply_to.sender
        except (KeyError, Message.DoesNotExist):
            reply_to = None
            receiver = None

        if not reply_to and 'receiver' not in attrs.keys():
            return {'success': False, 'error': 'Missing receiver or reply_to'}

        if not receiver:
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

        Message.send(sender, receiver, attrs['subject'], attrs['text'], reply_to=reply_to)
        return {'success': True}


class MessagesAction(BaseHandler):
    allowed_methods = ('POST', )

    def do_action(self, msg):
        raise NotImplemented

    def create(self, request, id):
        receiver = request.user.get_profile()
        msg = Message.objects.filter(id=id, receiver=receiver)
        if not msg.count():
            return {'success': False, 'error': 'No such message'}

        msg = msg.get()
        self.do_action(msg)
        return {'success': True}


class MessagesSetread(MessagesAction):
    def do_action(self, msg):
        return msg.set_read()


class MessagesSetunread(MessagesAction):
    def do_action(self, msg):
        return msg.set_unread()


class MessagesArchive(MessagesAction):
    def do_action(self, msg):
        return msg.archive()


class MessagesUnarchive(MessagesAction):
    def do_action(self, msg):
        return msg.unarchive()


class CastHandler(BaseHandler):
    allowed_methods = ('POST',)

    def create(self, request, player_id):
        player = request.user.get_profile()
        try:
            destination = Player.objects.get(pk=player_id)
        except Player.DoesNotExist:
            return rc.NOT_FOUND

        attrs = self.flatten_dict(request.POST)

        if 'spell' not in attrs.keys():
            return {'success': False, 'error': 'Missing spell'}

        try:
            spell = Spell.objects.get(pk=attrs['spell'])
            assert spell in [s.spell for s in player.magic.spells_available]
        except (Spell.DoesNotExist, AssertionError):
            return {'success': False, 'error': 'No such spell available'}

        try:
            days = int(attrs.get('days', 0))
            assert (days <= spell.due_days) and (spell.due_days <= 0 or days >= 1)
        except (ValueError, AssertionError):
            return {'success': False, 'error': 'Invalid days parameter'}

        due = datetime.now() + timedelta(days=days)
        error =  destination.magic.cast_spell(spell, source=player, due=due)
        if error is not None:
            return {'succes': False, 'error': 'Cast failed, %s' % error}

        return {'success': True}


class TopRaces(BaseHandler):
    allowed_methods = ('GET',)

    def read(self, request):
        races = [{'name': r.name, 'points': r.points, 'title': r.title or r.name, 'id': r.id} for r in Race.objects.all()]
        races.sort(key=lambda o: o['points'], reverse=True)

        return races


class TopGroups(BaseHandler):
    allowed_methods = ('GET',)

    def read(self, request, race_id=None):
        if race_id:
            try:
                race = Race.objects.get(pk=race_id)
            except Race.DoesNotExist:
                return rc.NOT_FOUND
            qs = race.playergroup_set.all()
        else:
            qs = PlayerGroup.objects.all()

        groups = [{'name': g.name, 'id': g.id, 'points': g.points, 'title': g.title or g.name} for g in qs]
        groups.sort(key=lambda g: g['points'], reverse=True)

        return groups


class TopPlayers(BaseHandler):
    allowed_methods = ('GET',)

    def read(self, request, group_id=None, race_id=None):
        if race_id:
            try:
                race = Race.objects.get(pk=race_id)
            except Race.DoesNotExist:
                return rc.NOT_FOUND
            qs = race.player_set.all()
        elif group_id:
            try:
                group = PlayerGroup.objects.get(pk=group_id)
            except PlayerGroup.DoesNotExist:
                return rc.NOT_FOUND
            qs = group.players.all()
        else:
            qs = Player.objects.all()

        qs = qs.order_by('-points')

        return [dict(first_name=p.user.first_name, last_name=p.user.last_name, id=p.id, points=p.points,
                     level=p.level_no, avatar=player_avatar(p), display_name=unicode(p)) for p in qs]

class GroupHandler(BaseHandler):
    allowed_methods = ('GET',)

    def read(self, request, group_id, type=None):
        try:
            group = PlayerGroup.objects.get(pk=group_id)
        except PlayerGroup.DoesNotExist:
            return rc.NOT_FOUND

        gh = GroupHistory(group)
        fp, q = get_fullpath(request)

        if type is None: # General information
            return {
                'id': group.id,
                'name': group.name,
                'points': group.live_points,
                'members': group.players.count(),
                'rank': gh.position,
                'activity': '%sactivity/%s' % (fp, q),
                'evolution': '%sevolution/%s' % (fp, q),
                }
        elif type == 'activity':
            qs = Activity.get_group_activiy(group)
            return [dict(user_from=unicode(a.user_from), user_to=unicode(a.user_to), message=a.message, date=a.timestamp) for a in qs]
        elif type == 'evolution':
            return gh.week_evolution()


class GroupsHandler(BaseHandler):
    allowed_methods = ('GET',)

    def read(self, request, race_id=None):
        if race_id is None:
            qs = PlayerGroup.objects.filter(owner=None).order_by('name')
        else:
            qs = PlayerGroup.objects.filter(owner=None, parent__id=race_id).order_by('name')
        return [dict(id=g.id, name=g.name, race_id=g.parent.id if g.parent else None, members=g.players.count()) for g in qs]


class RacesHandler(BaseHandler):
    allowed_methods = ('GET',)

    def read(self, request):
        qs = Race.objects.all().order_by('name')
        return [dict(id=r.id, name=r.name, members=r.player_set.count(), can_play=r.can_play) for r in qs]


class CategoryTagsHandler(BaseHandler):
    allowed_methods = ('GET',)

    def read(self, request, category):
        category = get_object_or_404(Category, name=category)
        tags = category.tag_set.all()
        return tags


class LessonCategoryTagsHandler(BaseHandler):
    allowed_methods = ('GET',)

    def read(self, request, category):
        category = get_object_or_404(LessonCategory, name=category)
        tags = category.tags.all()
        return tags


class MembersMixin(object):
    def to_dict(self, player):
        return dict(first_name=player.user.first_name, last_name=player.user.last_name, id=player.id, points=player.points,
                    level=player.level_no, avatar=player_avatar(player), display_name=unicode(player))


class RaceMembersHandler(BaseHandler, MembersMixin):
    allowed_methods = ('GET',)

    def read(self, request, race_id):
        race = get_object_or_404(Race, pk=race_id)

        return [self.to_dict(p) for p in race.player_set.order_by('-full_name')]


class GroupMembersHandler(BaseHandler, MembersMixin):
    allowed_methods = ('GET',)

    def read(self, request, group_id):
        group = get_object_or_404(PlayerGroup, pk=group_id)

        return [self.to_dict(p) for p in group.players.order_by('-full_name')]
