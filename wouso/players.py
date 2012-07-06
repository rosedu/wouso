from wouso.core.user.models import *

def players():
    for i in range(10):
        a = User()
        a.set_password("jika")
        a.username = "jika" + str(i) 
        a.save()


