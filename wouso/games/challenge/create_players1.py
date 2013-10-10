
from wouso.core.user.models import User
from wouso.core.user.models import Race
from wouso.core.user.models import Player

for i in range(1):
  Player.objects.all().delete()


