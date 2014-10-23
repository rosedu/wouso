from django.contrib import messages
from django.utils.translation import ugettext as _
from django.contrib.auth.decorators import login_required
from django.template import RequestContext
from django.template.loader import render_to_string
from django.views.generic import View
from django.shortcuts import render_to_response, redirect, get_object_or_404
from django.core.urlresolvers import reverse_lazy, reverse
from django.http import HttpResponseRedirect

from models import Quiz, QuizUser, QuizGame
from forms import QuizForm
from wouso.core.ui import register_sidebar_block


@login_required
def index(request):
    """ Shows all quizzes related to the current user """
    quizzes = Quiz.objects.filter()
    inactive_quizzes = [q for q in quizzes if q.elapsed]
    active_quizzes = [q for q in quizzes if q.is_active]
    return render_to_response('quiz/index.html',
                              {'active_quizzes': active_quizzes,
                               'inactive_quizzes': inactive_quizzes},
                              context_instance=RequestContext(request))


class QuizView(View):
    def dispatch(self, request, *args, **kwargs):
        if QuizGame.disabled():
            return redirect('wouso.interface.views.homepage')

        profile = request.user.get_profile()
        self.quiz_user = profile.get_extension(QuizUser)
        self.quiz = get_object_or_404(Quiz, pk=kwargs['id'])

        # check if user has already played quiz
        if self.quiz_user in self.quiz.players.all():
            messages.error(request, _('You have already submitted this'
                                      ' quiz!'))
            return HttpResponseRedirect(reverse('quiz_index_view'))

        # check if user has another quiz in progress
        if (self.quiz_user.start is not None) and (self.quiz_user.started_quiz_id != int(kwargs['id'])):
            messages.error(request, _('You have already started a quiz! '
                'Please submit it before starting another.'))
            return HttpResponseRedirect(reverse('quiz_index_view'))

        return super(QuizView, self).dispatch(request, *args, **kwargs)

    def get(self, request, *args, **kwargs):
        form = QuizForm(self.quiz)

        if not self.quiz.is_started_for_user(self.quiz_user):
            self.quiz.set_start(self.quiz_user)

        seconds_left = self.quiz.time_for_user(self.quiz_user)
        # set ID of current started quiz
        self.quiz_user.started_quiz_id = kwargs['id']
        self.quiz_user.save()

        return render_to_response('quiz/quiz.html',
                                  {'quiz': self.quiz, 'form': form, 'seconds_left': seconds_left},
                                  context_instance=RequestContext(request))

    def post(self, request, **kwargs):
        form = QuizForm(self.quiz, request.POST)
        results = form.get_response()
        form.check_self_boxes()

        # add player to the list of quiz players
        self.quiz.add_player(self.quiz_user)
        # reset start time and ID of current started quiz
        self.quiz.reset(self.quiz_user)

        results = Quiz.calculate_points(results)
        return render_to_response(('quiz/result.html'),
                                  {'quiz': self.quiz, 'points': results['points']},
                                  context_instance=RequestContext(request))


quiz = login_required(QuizView.as_view())


def sidebar_widget(context):
    user = context.get('user', None)
    if not user or not user.is_authenticated():
        return ''

    number_of_active_quizzes = Quiz.get_active_quizzes().__len__()

    return render_to_string('quiz/sidebar.html',
                            {'number_of_active_quizzes': number_of_active_quizzes}
                             )


register_sidebar_block('quiz', sidebar_widget)
