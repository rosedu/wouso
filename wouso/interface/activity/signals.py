from django.dispatch import Signal

addActivity = Signal(providing_args=['request', 'user'])
