from django.contrib import messages
from django.utils.translation import ugettext as _
from django.contrib.auth.decorators import login_required
from django.template import RequestContext
from django.template.loader import render_to_string
from django.views.generic import View
from django.shortcuts import render_to_response, redirect, get_object_or_404
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect
from games.quiz.models import QuizAttempt

from models import Quiz, QuizUser, QuizGame, UserToQuiz
from forms import QuizForm
from wouso.core.ui import register_sidebar_block


@login_required
def index(request):
    """ Shows all quizzes related to the current user """
    profile = request.user.get_profile()
    quiz_user = profile.get_extension(QuizUser)

    for q in Quiz.objects.all():
        try:
            obj = UserToQuiz.objects.get(user=quiz_user, quiz=q)
        except UserToQuiz.DoesNotExist:
            obj = UserToQuiz(user=quiz_user, quiz=q)
            obj.save()

    return render_to_response('quiz/index.html',
                              {'active_quizzes': quiz_user.active_quizzes,
                              'expired_quizzes': quiz_user.expired_quizzes},
                              context_instance=RequestContext(request))


class QuizView(View):
    def dispatch(self, request, *args, **kwargs):
        if QuizGame.disabled():
            return redirect('wouso.interface.views.homepage')

        profile = request.user.get_profile()
        self.quiz_user = profile.get_extension(QuizUser)
        self.quiz = get_object_or_404(Quiz, pk=kwargs['id'])
        self.through = UserToQuiz.objects.get(user=self.quiz_user, quiz=self.quiz)

        # check if user has already played quiz
        if not self.through.can_play_again():
            messages.error(request, _('You have already submitted this quiz!'))
            return HttpResponseRedirect(reverse('quiz_index_view'))

        return super(QuizView, self).dispatch(request, *args, **kwargs)

    def get(self, request, *args, **kwargs):
        form = QuizForm(self.quiz)

        if self.through.is_not_running():
            self.through.set_running()

        seconds_left = self.through.time_left

        return render_to_response('quiz/quiz.html',
                                  {'quiz': self.quiz, 'form': form,
                                  'seconds_left': seconds_left},
                                  context_instance=RequestContext(request))

    def post(self, request, **kwargs):
        form = QuizForm(self.quiz, request.POST)
        results = form.get_response()
        form.check_self_boxes()

        results = self.quiz.calculate_points(results)
        self.through.set_played(points=results['points'])

        return render_to_response('quiz/result.html',
                                  {'quiz': self.quiz, 'points': results['points']},
                                  context_instance=RequestContext(request))


quiz = login_required(QuizView.as_view())


def sidebar_widget(context):
    user = context.get('user', None)
    if not user or not user.is_authenticated():
        return ''

    quiz_user = user.get_profile().get_extension(QuizUser)
    number_of_active_quizzes = quiz_user.active_quizzes.__len__()

    return render_to_string('quiz/sidebar.html',
                            {'number_of_active_quizzes': number_of_active_quizzes})


register_sidebar_block('quiz', sidebar_widget)
