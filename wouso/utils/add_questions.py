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


def add_question(question):
    """ question is a dictionary with the following keys:
        'text': the question text (string)
        'answer_type': whether the question is single choice or multiple choice (string)
        'answers': a dictionary of answers with the following keys:
            'text': the answer text (string)
            'correct': whether the answer is correct (boolean)
        'proposed_by': the user that proposed the question (User object)
        'endorsed_by': the user endorsing the question (User object)
        'active': whether the question is active (boolean)
        'category': the question category (i.e. quiz) (Category object)
        'tag': the question primary tag (from file name) (Tag object)
        'file_tags': secondary tags (from file contents) (array of Tag objects)
    """
    q = Question()
    q.save()
    q.text = question['text']
    q.answer_type = question['answer_type']
    q.save()

    if question['proposed_by']:
        q.proposed_by = question['proposed_by']
    q.save()

    if question['endorsed_by']:
        q.endorsed_by = question['endorsed_by']
    q.save()

    q.active = question['active']

    if question['category']:
        q.category = question['category']
    q.save()

    if question['tag']:
        q.tags.add(question['tag'])
        q.save()

    if question['file_tags']:
        for tag in question['file_tags']:
            q.tags.add(tag)
        q.save()

    for answer in question['answers']:
        a = Answer(question=q, **answer)
        a.save()

    return q


START_QUESTION_MARK = "?"
ANSWER_TYPE_SINGLE_CHOICE = "R"
ANSWER_TYPE_MULTIPLE_CHOICE = "C"
ANSWER_TYPE_FREE_TEXT = "F"
START_CORRECT_ANSWER_MARK = "+"
START_INCORRECT_ANSWER_MARK = "-"
START_TAGS_MARK = "tags:"

def import_questions_from_file(f, proposed_by=None, endorsed_by=None, category=None, tag=None, active=False):
    # read file and parse contents
    a_saved = True
    q_saved = True
    a = {}
    answers = []
    q = {}
    num_correct_answers = 0
    num_imported_questions = 0
    state = 'question'

    for line in f:
        line = line.strip()
        if not line:
            continue

        # In case of start with question line, do the following:
        #    TODO: Explain the way parsing is done.
        if line.startswith(START_QUESTION_MARK):
            if not a_saved:
                answers.append(a)
                a_saved = True
            if not q_saved:
                if len(answers) == 0:
                    q['answer_type'] = ANSWER_TYPE_FREE_TEXT
                elif num_correct_answers <= 1:
                    q['answer_type'] = ANSWER_TYPE_SINGLE_CHOICE
                else:
                    q['answer_type'] = ANSWER_TYPE_MULTIPLE_CHOICE
                q['active'] = active
                q['answers'] = answers
                q['proposed_by'] = proposed_by
                q['endorsed_by'] = endorsed_by
                q['category'] = category
                q['tag'] = tag
                q['file_tags'] = file_tags
                ret = add_question(q)
                print "Added question id %d." %(ret.id)
                num_imported_questions += 1
                q_saved = True
                a_saved = True

            # Mark states for start of a new question.
            state = 'question'
            q = {}
            file_tags = None
            answers = []
            num_correct_answers = 0
            q_saved = False
            q['text'] = line[len(START_QUESTION_MARK):].strip()

        elif line.startswith(START_TAGS_MARK):
            tags_list = line.split(START_TAGS_MARK)[1]
            file_tag_names = [tag.strip() for tag in tags_list.split()]
            file_tags = []
            for tag_name in file_tag_names:
                try:
                    tag = Tag.objects.get(name=tag_name)
                except Exception as e:
                    continue
                if not tag:
                    continue
                file_tags.append(tag)

        elif line.startswith(START_CORRECT_ANSWER_MARK) or line.startswith(START_INCORRECT_ANSWER_MARK):
            if not a_saved:
                answers.append(a)
                a_saved = True

            state = 'answer'
            a = {}
            a_saved = False

            if line.startswith(START_INCORRECT_ANSWER_MARK):
                a['correct'] = False
                a['text'] = line[len(START_INCORRECT_ANSWER_MARK):].strip()
            else:
                a['correct'] = True
                a['text'] = line[len(START_CORRECT_ANSWER_MARK):].strip()
                num_correct_answers +=1

        else:
            # If nothing else, it's a continuation line.
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
        if len(answers) == 0:
            q['answer_type'] = ANSWER_TYPE_FREE_TEXT
        elif num_correct_answers <= 1:
            q['answer_type'] = ANSWER_TYPE_SINGLE_CHOICE
        else:
            q['answer_type'] = ANSWER_TYPE_MULTIPLE_CHOICE
        q['active'] = active
        q['answers'] = answers
        q['proposed_by'] = proposed_by
        q['endorsed_by'] = endorsed_by
        q['category'] = category
        q['tag'] = tag
        q['file_tags'] = file_tags
        ret = add_question(q)
        print "Added question id %d." %(ret.id)
        num_imported_questions += 1
        q_saved = True
        a_saved = True

    return num_imported_questions


def main():
    if len(sys.argv) != 5:
        print >>sys.stderr, 'Usage: add_questions.py <file> <category> <proposed-by> <endorsed_by>'
        sys.exit(1)

    filename = sys.argv[1]
    category_name = sys.argv[2]
    proposed_by_name = sys.argv[3]
    endorsed_by_name = sys.argv[4]
    # Tag is filename without extension.
    tag_name = os.path.splitext(os.path.basename(filename))[0]

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
        print >>sys.stderr, "Endorsed by user %s does not exist." %(endorsed_by_name)
        sys.exit(1)
    if not endorsed_by:
        print >>sys.stderr, "Endorsed by user %s does not exist." %(endorsed_by_name)
        sys.exit(1)

    try:
        category = Category.objects.get(name=category_name)
    except Exception as e:
        print e
        print >>sys.stderr, "Category %s does not exist." %(category_name)
        sys.exit(1)
    if not category:
        print >>sys.stderr, "Category %s does not exist." %(category_name)
        sys.exit(1)

    try:
        tag = Tag.objects.get(name=tag_name)
    except Exception as e:
        print e
        print >>sys.stderr, "Tag %s does not exist." %(tag_name)
        sys.exit(1)
    if not tag:
        print >>sys.stderr, "Tag %s does not exist." %(tag_name)
        sys.exit(1)

    try:
        f = codecs.open(filename, 'r', 'utf-8')
    except:
        print >>sys.stderr, "Cannot open file %s for reading questions." %(filename)
        sys.exit(1)

    print "Import questions from file %s." %(filename)
    print "  Category: %s" %(category)
    print "  Tag: %s" %(tag)
    print "  Proposed by: %s" %(proposed_by)
    print "  Endorsed by: %s" %(endorsed_by)

    n = import_questions_from_file(f, proposed_by, endorsed_by, category, tag, active=True)
    print "\nImported %d questions." %(n)


if __name__ == '__main__':
    sys.exit(main())
