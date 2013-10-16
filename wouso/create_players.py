from wouso.core.user.models import User
from wouso.core.user.models import Race

for i in range(50):
    name = 'student' + str(i + 1)
    user = User.objects.create(username=name)
    user.set_password('student')
    user.save()
    rasa = Race.objects.all()[1]
    pl = user.get_profile()
    pl.race = rasa
    pl.full_name = 'Student' + str(i)
    pl.points = i * 50
    pl.save()
