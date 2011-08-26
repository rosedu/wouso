#!/usr/bin/env python

import codecs
import sys
from django.core.management import setup_environ


def init():
    import settings
    setup_environ(settings)


def add(question, answers, tags=[]):
    ''' question is a dict with the following keys: text, endorsed_by, answer_type
    [, proposed_by, active, type, code]
    answers is a list of dicts with the following keys: text, correct [, explanation]
    '''

    # imports valid only after init()
    from wouso.core.qpool.models import Question, Answer

    #print question
    #for a in answers:
    #    print a

    # create and save question
    q = Question(**question)
    q.save()

    if len(tags) > 0:
        for tag in tags:
            q.tags.add(tag)
        q.save()

    # create and save answers for question
    for answer in answers:
        a = Answer(question=q, **answer)
        a.save()


def import_from_file(opened_file, proposed_by, tags=[]):
    # read file and parse contents
    a_saved = True
    q_saved = True

    for line in opened_file:
        line = line.strip() + '\n'

        # blank line
        if not line:
            continue

        # parse line according to its beginning
        if line[0] == '?':
            if not a_saved:
                answers.append(a)
                a_saved = True
            if not q_saved:
                q['proposed_by'] = proposed_by
                add(q, answers, tags)
                q_saved = True
                a_saved = True

            state = 'question'
            q = {}
            answers = []
            q_saved = False
            s = line.split()

            if s[1] == 'S' or s[1] == 's':
                q['answer_type'] = 'R'
            else:
                q['answer_type'] = 'C'

            q['text'] = ' '.join(s[2:])


        elif line[0] == '-' or line[0] == '+':
            if not a_saved:
                answers.append(a)
                a_saved = True

            state = 'answer'
            a = {}
            a_saved = False
            s = line.split()

            if s[0] == '-':
                a['correct'] = False
            else:
                a['correct'] = True

            a['text'] = ' '.join(s[1:])

        else:
            # continuation line
            if state == 'question':
                q['text'] += (line)

            else:
                a['text'] += (line)

    if not a_saved:
        answers.append(a)
        a_saved = True
    if not q_saved:
        q['proposed_by'] = proposed_by
        add(q, answers, tags)


def main():

    if len(sys.argv) != 3:
        print 'Usage: add_questions.py <file> <endorsed_by>'
        sys.exit(1)

    try:
        init()
    except:
        print "No wouso/settings.py file. Maybe you can symlink the example file?"
        sys.exit(1)

    from django.contrib.auth.models import User
    proposed_by = User.objects.get(username__exact=sys.argv[2])

    with codecs.open(sys.argv[1], 'r', 'utf-8') as f:
        import_from_file(f, proposed_by)

    print 'Done.'


if __name__ == '__main__':
    main()
