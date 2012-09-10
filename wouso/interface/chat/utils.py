import array
import random
from wouso.interface.chat.models import ChatUser

def shuffle_text(text):
    if isinstance(text, unicode):
        temp = array.array('u', text)
        converter = temp.tounicode
    else:
        temp = array.array('c', text)
        converter = temp.tostring
    random.shuffle(temp)
    return converter()


def change_text(text):
    text = text.split(" ")
    random.shuffle(text)
    new_text = ""
    for world in text:
        if len(world) > 3:
            new_text = new_text + world[0] + shuffle_text(world[1:len(world)-1]) + world[len(world)-1] + " "
        else:
            new_text = new_text + world + " "
    return new_text


def get_author(request):
    return request.user.get_profile().get_extension(ChatUser)