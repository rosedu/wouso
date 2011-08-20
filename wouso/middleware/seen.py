import logging
from datetime import datetime

class Seen:
    def process_request(self, request):
        if not request.user.is_anonymous():
            profile = request.user.get_profile()
            logging.debug('seen' + str(profile))
            if profile:
                profile.last_seen = datetime.now()
                profile.save()
        return None
