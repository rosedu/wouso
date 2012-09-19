from django.dispatch import Signal
from Achievements import check_for_achievements
""" Register new signal """
addActivity = Signal(providing_args=['request'])
messageSignal = Signal()
messageSignal.connect(check_for_achievements)
