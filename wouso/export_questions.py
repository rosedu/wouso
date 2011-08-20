#!/usr/bin/env python

import codecs
import sys
from django.core.management import setup_environ


def init():
    import settings
    setup_environ(settings)


def main():

    if len(sys.argv) != 2:
        print 'Usage: export.py <file>'
        sys.exit(1)

    try:
        init()
    except:
        print "No wouso/settings.py file. Maybe you can symlink the example file?"
        sys.exit(1)

    from wouso.core.qpool.models import Question, Answer

    with codecs.open(sys.argv[1], 'w', 'utf-8') as f:

        for question in Question.objects.all():
            if question.answer_type == 'R':
                type = 'S'
            else:
                type = 'M'
            f.write('? ' + type + ' ' + question.text + '\n')

            for answer in question.answers.all():
                if answer.correct is False:
                    type = '-'
                else:
                    type = '+'
                f.write(type + ' ' + answer.text + '\n')

    print 'Done.'


if __name__ == '__main__':
    main()
