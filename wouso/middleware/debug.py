import logging
from django.conf import settings

class DebugExceptionMiddleware(object):
    """ Throw 500 exceptions to the console.
    """
    def process_exception(self, request, exception):
        if settings.DEBUG:
            logging.basicConfig(level=logging.INFO)
            logging.exception(exception)
            logging.info("POST:")
            logging.info(request.POST)
            logging.info("META")
            logging.info(request.META)
