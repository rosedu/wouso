# python imports & django environment setup
from sys import argv
import json
from django.core.management import setup_environ
import settings
setup_environ(settings)

# django imports
from django.core import serializers
from django.contrib.contenttypes.models import ContentType

# Models to be dumped/restored
from django.contrib.auth.models import User
from wouso.core.magic.models import Artifact, ArtifactGroup
from wouso.core.qpool.models import Question, Answer, Tag
from wouso.games.quest.models import Quest


def dump_db():
    dump_file = open('../contrib/db_dump.json', 'w')
    models_list = [User, Tag, Question, Answer, ArtifactGroup, Artifact, Quest]
    all_objects = []
    for model in models_list:
        all_objects = all_objects + list(model.objects.all())
    json_serializer = serializers.get_serializer("json")()
    json_serializer.serialize(all_objects, ensure_ascii=True, stream=dump_file)
    dump_file.close()

def restore_db():
    dec = json.JSONDecoder()
    dump_file = open('../contrib/db_dump.json', 'r')
    data_list = dec.decode(dump_file.read())
    for elem in data_list:
        l = elem['model'].split('.')
        object = ContentType.objects.get(app_label=l[0], model=l[1]).model_class()()
        object.pk = elem['pk']
        for key, value in elem['fields'].iteritems():
            if hasattr(object, key):
                setattr(object,key,value)
            elif hasattr(object, '%s_id' % key):
                setattr(object,'%s_id' % key,value)
            else:
                print('%s does not have attribute %s' % (elem['model'], key))
        object.save()

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
