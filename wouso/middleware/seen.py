from datetime import datetime
from wouso.core import signals

class Seen:
    def process_request(self, request):
#        import pprint; pprint.pprint(request.META['HTTP_AUTHORIZATION']);pprint.pprint(request.POST);
        if not request.user.is_anonymous():
            try:
                profile = request.user.get_profile()
            except:
                profile = None

            if profile:
                if not profile.last_seen or profile.last_seen.hour != datetime.now().hour:
                    # Signal a new hour seen
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
