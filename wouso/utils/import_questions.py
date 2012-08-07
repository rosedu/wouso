# This has to be used from the wouso folder like so:
# PYTHONPATH=. python utils/import_questions

import codecs
import sys
from django.core.management import setup_environ


def init():
    import settings
    setup_environ(settings)


def add(question, answers, category=None, tags=[]):
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

    if category is not None:
        q.category = category
        q.save()

    # create and save answers for question
    for answer in answers:
        a = Answer(question=q, **answer)
        a.save()

    return q


def import_from_file(opened_file, proposed_by=None, endorsed_by=None, category=None, tags=[], all_active=False):
    # read file and parse contents
    a_saved = True
    q_saved = True
    a = {}
    answers = []
    q = {}
    nr_correct = 0

    nr_imported = 0


    state = 'question'

    for line in opened_file:
        line = line.strip()
        if not line:
            continue

        # parse line according to its beginning
        # second condition (or ____) is for windows reasons
        if line[0] == '?' or (ord(line[0]) == 239 and line[3] == '?'):
            if not a_saved:
                answers.append(a)
                a_saved = True
            if not q_saved:
                if all_active is True:
                    q['active'] = True
                if endorsed_by is not None:
                    q['endorsed_by'] = endorsed_by
                if proposed_by is not None:
                    q['proposed_by'] = proposed_by
                if len(answers) == 0:
                    q['answer_type'] = 'F'
                elif nr_correct == 1:
                    q['answer_type'] = 'R'
                else:
                    q['answer_type'] = 'C'
                add(q, answers, category, tags)
                nr_imported += 1
                q_saved = True
                a_saved = True

            state = 'question'
            q = {}
            answers = []
            nr_correct = 0
            q_saved = False
            s = line.split()

            q['text'] = ' '.join(s[1:])


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
                nr_correct += 1

            a['text'] = ' '.join(s[1:])

        else:
            # continuation line
            if state == 'question':
                if q.has_key('text'):
                    q['text'] += '\n' + line
                else:
                    q['text'] = line

            else:
                a['text'] += '\n' + line

    if not a_saved:
        answers.append(a)
        a_saved = True
    if not q_saved:
        if all_active is True:
            q['active'] = True
        if endorsed_by is not None:
            q['endorsed_by'] = endorsed_by
        if proposed_by is not None:
            q['proposed_by'] = proposed_by
        if len(answers) == 0:
            q['answer_type'] = 'F'
        elif nr_correct == 1:
            q['answer_type'] = 'R'
        else:
            q['answer_type'] = 'C'
        add(q, answers, category, tags)
        nr_imported += 1

    return nr_imported


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
