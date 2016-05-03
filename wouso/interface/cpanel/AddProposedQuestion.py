import datetime
from django import forms
from django.conf import settings
from django.contrib import messages
from django.contrib.auth import models as auth
from django.contrib.auth.decorators import permission_required
from django.contrib.auth.models import User, Group
from django.core.cache import cache
from django.core.exceptions import ValidationError
from django.core.paginator import Paginator, EmptyPage, InvalidPage
from django.core.urlresolvers import reverse, reverse_lazy
from django.db.models import Q
from django.http import HttpResponseRedirect, HttpResponse
from django.shortcuts import get_object_or_404, redirect, render_to_response
from django.template import RequestContext
from django.template.defaultfilters import slugify
from django.utils.translation import ugettext_noop
from django.utils.translation import ugettext as _
from django.views.generic import UpdateView, CreateView, ListView, FormView, \
    TemplateView, DetailView
from wouso.core.config.models import Setting, IntegerSetting, IntegerListSetting
from wouso.core.decorators import staff_required
from wouso.core.ui import get_sidebar
from wouso.core.user.models import Player, PlayerGroup, Race
from wouso.core.magic.models import Artifact, ArtifactGroup, Spell
from wouso.core.qpool.models import Schedule, Question, Tag, Category, Answer, ProposedQuestion
from wouso.core.qpool import get_questions_with_category
from wouso.core.god import God
from wouso.core import scoring
from wouso.core.scoring.models import Formula, History, Coin
from wouso.core.signals import addActivity, add_activity
from wouso.core.security.models import Report
from wouso.games.challenge.models import Challenge, Participant
from wouso.interface.activity.models import Activity
from wouso.interface.apps.messaging.models import Message
from wouso.interface.apps.pages.models import StaticPage, NewsItem
from wouso.interface.cpanel.models import Customization, Switchboard, \
    GamesSwitchboard
from wouso.interface.forms import InstantSearchForm
from wouso.interface.apps.qproposal import QUEST_GOLD, CHALLENGE_GOLD, QOTD_GOLD
from wouso.middleware.impersonation import ImpersonateMiddleware
from wouso.utils.import_questions import import_from_file
from forms import TagsForm, UserForm, SpellForm, AddTagForm,\
    EditReportForm, RaceForm, PlayerGroupForm, RoleForm, \
    StaticPageForm, NewsForm, KarmaBonusForm, AddQuestionForm, EditQuestionForm, \
    FormulaForm, TagForm, ChangePasswordForm, AddUserForm


"""Add ProposedQuestion objects in db """


quest = Category.objects.get(name = 'quest')
quiz = Category.objects.get(name = 'quiz')
workshop = Category.objects.get(name = 'workshop')
challenge = Category.objects.get(name = 'challenge')
specialchalllenge = Category.objects.get(name = 'specialchallenge')
qotd = Category.objects.get(name = 'qotd')

answers = json.dumps([{'text': 'answer1', 'correct': False},
					{"text": "answer2", "correct": False},
					{"text": "answer3", "correct": True},
					{"text": "answer4", "correct": False}])

admin = User.objects.get(username='admin')



