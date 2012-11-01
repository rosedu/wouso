from django.dispatch import Signal
""" Register new signal """
addActivity = Signal(providing_args=['request'])
addedActivity = Signal()
messageSignal = Signal()
