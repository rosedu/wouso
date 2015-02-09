from piston.handler import BaseHandler
from piston.utils import rc
from wouso.core.user.models import Player
from models import ChallengeUser, ChallengeGame, ChallengeException, Challenge


class ChallengesHandler(BaseHandler):
    methods_allowed = ('GET',)

    def read(self, request):
        player = request.user.get_profile()
        challuser = player.get_extension(ChallengeUser)
        return [dict(status=c.status, date=c.date, id=c.id,
                     user_from=unicode(c.user_from.user),
                     user_from_id=c.user_from.user.id,
                     user_to=unicode(c.user_to.user),
                     user_to_id=c.user_to.user.id) for c in ChallengeGame.get_active(challuser)]


class ChallengeGetRandom(BaseHandler):
    methods_allowed = ('GET',)

    def read(self, request):
        challuser = (request.user.get_profile()).get_extension(ChallengeUser)
        challuser2 = challuser.get_random_opponent()
        if not challuser2:
            return {'succes': False, 'error': 'No random opponent found'}
        try:
            chall = challuser.launch_against(challuser2)
        except ChallengeException as e:
            return {'succes': False, 'error': unicode(e)}
        return {'succes': True, 'challenge': dict(id=chall.id)}


class ChallengeLaunch(BaseHandler):
    methods_allowed = ('GET',)

    def read(self, request, player_id):
        player = request.user.get_profile()
        challuser = player.get_extension(ChallengeUser)

        try:
            player2 = Player.objects.get(pk=player_id)
        except Player.DoesNotExist:
            return rc.NOT_FOUND

        challuser2 = player2.get_extension(ChallengeUser)

        try:
            chall = challuser.launch_against(challuser2)
        except ChallengeException as e:
            return {'success': False, 'error': unicode(e)}

        return {'success': True, 'challenge': dict(id=chall.id)}


class ChallengeHandler(BaseHandler):
    methods_allowed = ('GET',)

    def read(self, request, challenge_id, action='play'):
        player = request.user.get_profile()
        challuser = player.get_extension(ChallengeUser)
        try:
            challenge = Challenge.objects.get(pk=challenge_id)
        except Challenge.DoesNotExist:
            return rc.NOT_FOUND

        try:
            participant = challenge.participant_for_player(player)
        except ValueError:
            return rc.NOT_FOUND

        if action == 'play':
            if not challenge.is_runnable():
                return {'success': False, 'error': 'Challenge is not runnable'}

            if not participant.start:
                challenge.set_start(player)

            if challenge.is_expired_for_user(player):
                return {'success': False, 'error': 'Challenge expired for this user'}

            return {'success': True,
                    'status': challenge.status,
                    'from': unicode(challenge.user_from.user),
                    'to': unicode(challenge.user_to.user),
                    'date': challenge.date,
                    'seconds': challenge.time_for_user(challuser),
                    'questions': dict(
                        [(q.id, {'text': q, 'answers': dict([(a.id, a) for a in q.answers])}) for q in
                         challenge.questions.all()]),
            }

        if action == 'refuse':
            if challenge.user_to.user == challuser and challenge.is_launched():
                challenge.refuse()
                return {'success': True}
            else:
                return {'success': False, 'error': 'Cannot refuse this challenge'}
        if action == 'cancel':
            if challenge.user_from.user == challuser and challenge.is_launched():
                challenge.cancel()
                return {'success': True}
            else:
                return {'success': False, 'error': 'Cannot cancel this challenge'}
        if action == 'accept':
            if challenge.user_to.user == challuser and challenge.is_launched():
                challenge.accept()
                return {'success': True}
            else:
                return {'success': False, 'error': 'Cannot accept this challenge'}

        return {'success': False, 'error': 'Unknown action'}

    def create(self, request, challenge_id):
        """ Attempt to respond
        """
        player = request.user.get_profile()
        challuser = player.get_extension(ChallengeUser)
        try:
            challenge = Challenge.objects.get(pk=challenge_id)
        except Challenge.DoesNotExist:
            return rc.NOT_FOUND

        try:
            p = challenge.participant_for_player(player)
        except ValueError:
            return rc.NOT_FOUND

        if p.played:
            return {'success': False, 'error': 'Already played'}

        data = self.flatten_dict(request.POST)
        responses = {}
        try:
            for q in challenge.questions.all():
                responses[q.id] = [int(a) if a else '' for a in data.get(str(q.id), '').split(',')]
        except (IndexError, ValueError):
            return {'success': False, 'error': 'Unable to parse answers'}

        result = challenge.set_played(challuser, responses)

        return {'success': True, 'result': result}
