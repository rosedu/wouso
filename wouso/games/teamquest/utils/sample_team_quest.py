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
    """Create objects if they do not exist. Show if objects are created or not."""
    print "Creating user with username %s if it does not exist." % ('_sample_teamquest_user')
    owner, created = User.objects.get_or_create(username='_sample_teamquest_user')
    owner.set_password('password')
    owner.save()
    owner = owner.get_profile().get_extension(TeamQuestUser)

    print "Creating group with name %s if it does not exist." % ('_sample_teamquest_group')
    try:
        group = TeamQuestGroup.objects.get(name='_sample_teamquest_group')
    except TeamQuestGroup.DoesNotExist:
        group = TeamQuestGroup.create(group_owner=owner, name='_sample_teamquest_group')

    try:
        quest = TeamQuest.objects.get(title="Sample Team Quest")
        print "Quest with title %s already exists. Assuming levels and questions are added so exiting." % ('Sample Team Quest')
        return
    except:
        pass

    print "Adding category %s if it does not exist." % ('teamquest')
    category = Category.add('teamquest')

    print "Adding 5 levels (15 questions, 15 answers) in category %s if they do not exist." % ('teamquest')
    number_of_levels = 5
    questions = []
    for index in range(number_of_levels * (number_of_levels + 1) / 2):
        question, created = Question.objects.get_or_create(text='question'+str(index+1), answer_type='F', category=category, active=True)
        questions.append(question)
        answer, created = Answer.objects.get_or_create(text='answer'+str(index+1), correct=True, question=question)

    print "Adding 5 team quest levels if they do no exist."
    levels = []
    # The start index of the questions sequence that goes in a level
    base = 0
    for index in range(number_of_levels):
        level = TeamQuestLevel.create(quest=None, bonus=0, questions=questions[base:base+number_of_levels-index])
        levels.append(level)
        base += number_of_levels - index

    print "Adding team quest with title %s using 5 levels and 15 questions." % ('Sample Team Quest')
    quest = TeamQuest.create(title="Sample Team Quest",
            start_time=datetime.datetime.now(),
            end_time=datetime.datetime(2030, 12, 25),
            levels=levels)


def status():
    try:
        user = User.objects.get(username='_sample_teamquest_user')
        print "User with username %s exists." % ('_sample_teamquest_user')
    except User.DoesNotExist:
        print "There is no user with username %s." % ('_sample_teamquest_user')

    try:
        group = TeamQuestGroup.objects.get(name='_sample_teamquest_group')
        print "Group with name %s exists." % ('_sample_teamquest_group')
    except TeamQuestGroup.DoesNotExist:
        print "There is no group with name %s." % ('_sample_teamquest_group')

    try:
        quest = TeamQuest.objects.filter(title="Sample Team Quest")
        print "Quest with title %s exists." % ("Sample Team Quest")
    except TeamQuest.DoesNotExist:
        print "There is no quest with title %s." % ('Sample Team Quest')

    try:
        category = Category.objects.get(name='teamquest')
        print "Category with name %s exists." % ('teamquest')
        question = Question.objects.filter(category=category)
        print "There are %d questions in category %s:" % (question.count(), category.name)
        for q in question:
            try:
                a = Answer.objects.get(question=q)
                print "  * %s (%s)" % (q, a)
            except Answer.DoesNotExist:
                pass
    except Category.DoesNotExist:
        print "There is no category with name %s." % ('teamquest')


def cleanup():
    """Delete items. If more than one item (should not be the case)
       delete all of them."""
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
    parser.add_argument("--delete", help="delete sample teamquest", action="store_true")
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
