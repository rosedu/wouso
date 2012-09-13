from datetime import datetime
from wouso.interface.activity import signals

class Seen:
    def process_request(self, request):
        if not request.user.is_anonymous():
            try:
                profile = request.user.get_profile()
            except:
                profile = None

            if profile:
                if not profile.last_seen or profile.last_seen.day != datetime.now().day:
                    # Signal a new day seen
                    signals.addActivity.send(sender=None,
                        game=None,
                        user_from=profile,
                        user_to=profile,
                        action='seen',
                        public=False,
                    )
                profile.last_seen = datetime.now()
                profile.save()
        return None
