from django.dispatch import Signal


""" Register new signal """
addActivity = Signal()
addedActivity = Signal()
messageSignal = Signal()
postCast = Signal()
postExpire = Signal()


def add_activity(player, text, **kwargs):
    """ Simplified addActivity signal.
    """
    addActivity.send(sender=None,
                     user_from=player,
                     user_to=player,
                     message=text,
                     arguments=kwargs,
                     game=None)
