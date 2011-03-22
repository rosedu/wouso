from sys import argv
from django.core.management import setup_environ
import settings
setup_environ(settings)
from django.core import serializers
from django.contrib.auth.models import User
from core.qpool.models import Question, Answer

json_serializer = serializers.get_serializer("json")()

def dump_db():
    dump_file = open('db_dump.txt', 'w')
    users = User.objects.all()
    qpool = Question.objects.all()
    qpool_answ = Answer.objects.all()
    all_objects = list(list(users) + list(qpool) + list(qpool_answ))
    json_serializer.serialize(all_objects, ensure_ascii=True, stream=dump_file)
    dump_file.close()

def restore_db():
    pass

def usage():
    print('Usage: %s command\n' % argv[0])
    print('Available commands:\n  dump\n  restore\n  help')

if __name__ == "__main__":
    if len(argv) == 2:
        if argv[1] == 'dump':
            dump_db()
        elif argv[1] == 'restore':
            restore_db()
        elif argv[1] == 'help':
            usage()
    else:
        usage()
