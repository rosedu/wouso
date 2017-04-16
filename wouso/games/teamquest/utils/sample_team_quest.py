#!/usr/bin/env/python

# To test, run from wouso folder using commands such as:
# PYTHONPATH=../:. python games/teamquest/utils/create_sample_team_quest.py

import argparse
import sys
import os
import codecs
import datetime

# Setup Django environment.
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "wouso.settings")

from django.contrib.auth.models import User
from wouso.core.user.models import Race
from wouso.core.user.models import Player
from wouso.games.teamquest.models import TeamQuest, TeamQuestLevel, TeamQuestStatus, TeamQuestUser, TeamQuestGroup, TeamQuestLevelStatus, TeamQuestQuestion
from wouso.core.qpool.models import Question, Answer, Category


def create():
    owner = User.objects.create(username='_sample_teamquest_user')
    owner.set_password('password')
    owner.save()
    owner = owner.get_profile().get_extension(TeamQuestUser)
    group = TeamQuestGroup.create(group_owner=owner, name='_sample_teamquest_group')
    category = Category.add('teamquest')

    number_of_levels = 5
    questions = []
    for index in range(number_of_levels * (number_of_levels + 1) / 2):
        question = Question.objects.create(text='question'+str(index+1), answer_type='F',
                category=category, active=True)
        questions.append(question)
        answer = Answer.objects.create(text='answer'+str(index+1), correct=True, question=question)

    levels = []
    # The start index of the questions sequence that goes in a level
    base = 0
    for index in range(number_of_levels):
        level = TeamQuestLevel.create(quest=None, bonus=0,
                questions=questions[base:base+number_of_levels-index])
        levels.append(level)
        base += number_of_levels - index

    quest = TeamQuest.create(title="Sample Team Quest", start_time=datetime.datetime.now(),
            end_time=datetime.datetime(2030,12,25), levels=levels)


def status():
    user = User.objects.filter(username='_sample_teamquest_user')
    print "There are %d users with username %s:" %(user.count(), '_sample_teamquest_user')
    for u in user:
        print "  *", u

    group = TeamQuestGroup.objects.filter(name='_sample_teamquest_group')
    print "There are %d groups with name %s." %(group.count(), '_sample_teamquest_group')
    for g in group:
        print "  *", g.name

    category = Category.objects.filter(name='teamquest')
    print "There are %d categories with name %s." %(category.count(), 'teamquest')
    for c in category:
        print "  *", c.name

    if category:
        question = Question.objects.filter(category=category[0])
        print "There are %d questions in category %s:" %(question.count(), category[0].name)
        for q in question:
            try:
                a = Answer.objects.get(question=q)
                print "  * %s (%s)" %(q, a)
            except:
                pass

    quest = TeamQuest.objects.filter(title="Sample Team Quest")
    print "There are %d quests with title %s:" %(quest.count(), "Sample Team Quest")
    for q in quest:
        print "  *", q.title


def cleanup():
    user = User.objects.filter(username='_sample_teamquest_user')
    for u in user:
        u.delete()
    category = Category.objects.filter(name='teamquest')
    for c in category:
        c.delete()
    quest = TeamQuest.objects.filter(title="Sample Team Quest")
    for q in quest:
        q.delete()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--create", help="create sample teamquest", action="store_true")
    parser.add_argument("--cleanup", help="cleanup sample teamquest", action="store_true")
    parser.add_argument("--status", help="show status of sampe teamquest objects", action="store_true")
    args = parser.parse_args()

    if args.create:
        create()

    if args.cleanup:
        cleanup()

    if args.status:
        status()


if __name__ == "__main__":
    sys.exit(main())
