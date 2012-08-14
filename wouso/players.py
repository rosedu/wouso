from wouso.core.user.models import *
from wouso.interface.chat.models import *
from wouso.interface.chat.views import *



def exista(names):
    try:
        print 'try'
        return ChatRoom.objects.get(name = names)
    except ChatRoom.DoesNotExist:
        print 'except'
        create_room(names)

def players():
    for i in range(10):
        a = User()
        a.set_password("jika")
        a.username = "jika" + str(i) 
        a.save()


