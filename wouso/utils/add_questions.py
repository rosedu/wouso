#!/usr/bin/env python

# To test, run from parent folder using a command such as:
# PYTHONPATH=../:. python utils/add_questions.py utils/sample-data/sample-questions.csv

import sys
import os
import codecs

# Setup Django environment.
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "wouso.settings")

from wouso.core.qpool.models import Question, Answer, Tag, Category
from django.contrib.auth.models import User


def add_question(question, answers, category=None, tags=None, file_tags=None):
    """ Question is a dict with the following keys: text, endorsed_by, answer_type
    [, proposed_by, active, type, code]
    answers is a list of dicts with the following keys: text, correct [, explanation]
    """
    q = Question(**question)
    q.save()

    if tags:
        for tag in tags:
            q.tags.add(tag)
        q.save()

    if file_tags:
        for tag_name in file_tags:
            tag, created = Tag.objects.get_or_create(name=tag_name, category=category)
            if created:
                tag.save()
                if category is not None:
                    category.tag_set.add(tag)
                    category.save()
            q.tags.add(tag)
        q.save()

    if category is not None:
        q.category = category
        q.save()

    for answer in answers:
        a = Answer(question=q, **answer)
        a.save()

    return q


def import_from_file(opened_file, proposed_by=None, endorsed_by=None, category=None, tags=None, all_active=False):
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
                add(q, answers, category, tags, file_tags)
                nr_imported += 1
                q_saved = True
                a_saved = True

            state = 'question'
            q = {}
            file_tags = None
            answers = []
            nr_correct = 0
            q_saved = False
            s = line.split()

            q['text'] = ' '.join(s[1:])

        elif line == 'tags:':
            continue

        elif line.startswith('tags: '):
            tags_line = line.split('tags: ')[1]
            file_tags = tags_line.split()

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
        add(q, answers, category, tags, file_tags)
        nr_imported += 1

    return nr_imported


def main():

    if len(sys.argv) != 4:
        print 'Usage: add_questions.py <file> <proposed-by> <endorsed_by>'
        sys.exit(1)

    filename = sys.argv[1]
    proposed_by_name = sys.argv[2]
    endorsed_by_name = sys.argv[3]

    try:
        proposed_by = User.objects.get(username=proposed_by_name)
    except Exception as e:
        print e
        print >>sys.stderr, "Proposed by user %s does not exist." %(proposed_by_name)
        sys.exit(1)
    if not proposed_by:
        print >>sys.stderr, "Proposed by user %s does not exist." %(proposed_by_name)
        sys.exit(1)

    try:
        endorsed_by = User.objects.get(username=endorsed_by_name)
    except Exception as e:
        print e
        print >>sys.stderr, "Proposed by user %s does not exist." %(endorsed_by_name)
        sys.exit(1)
    if not endorsed_by:
        print >>sys.stderr, "Proposed by user %s does not exist." %(endorsed_by_name)
        sys.exit(1)

    try:
        f = codecs.open(filename, 'r', 'utf-8')
    except:
        print >>sys.stderr, "Cannot open file %s for reading questions." %(filename)
        sys.exit(1)
    #import_questions_from_file(f, proposed_by, endorsed_by)


if __name__ == '__main__':
    sys.exit(main())
