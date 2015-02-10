from django.contrib import messages
from django.utils.translation import ugettext as _
from django.contrib.auth.decorators import login_required
from django.template import RequestContext
from django.template.loader import render_to_string
from django.views.generic import View
from django.shortcuts import render_to_response, redirect, get_object_or_404
from django.http import HttpResponseRedirect
from django.views.generic import ListView

from models import Quiz, QuizUser, QuizGame, UserToQuiz, QuizCategory
from forms import QuizForm
from wouso.core.ui import register_sidebar_block


class QuizIndexView(ListView):
    model = QuizCategory
    context_object_name = 'categories'
    template_name = 'quiz/index.html'


index = login_required(QuizIndexView.as_view())


class QuizCategoryView(ListView):
    model = Quiz
    template_name = 'quiz/category.html'

    def get_context_data(self, **kwargs):
        context = super(QuizCategoryView, self).get_context_data(**kwargs)
        profile = self.request.user.get_profile()
        quiz_user = profile.get_extension(QuizUser)

        for q in Quiz.objects.all():
            if not q.is_expired():
                q.update_status()
            try:
                obj = UserToQuiz.objects.get(user=quiz_user, quiz=q)
            except UserToQuiz.DoesNotExist:
                obj = UserToQuiz(user=quiz_user, quiz=q)
                obj.save()

        context['active_quizzes'] = quiz_user.active_quizzes
        context['inactive_quizzes'] = quiz_user.inactive_quizzes
        context['expired_quizzes'] = quiz_user.expired_quizzes
        context['played_quizzes'] = quiz_user.played_quizzes

        return context


category = login_required(QuizCategoryView.as_view())


class QuizView(View):
    def dispatch(self, request, *args, **kwargs):
        if QuizGame.disabled():
            return redirect('wouso.interface.views.homepage')

        profile = request.user.get_profile()
        self.quiz_user = profile.get_extension(QuizUser)
        self.quiz = get_object_or_404(Quiz, pk=kwargs['id'])
        self.through = UserToQuiz.objects.get(user=self.quiz_user, quiz=self.quiz)

        # check if user is eligible to play quiz
        if not self.through.can_play_again() and not self.quiz_user.user.is_staff:
            messages.error(request,
                           _('You can replay this quiz in {days} day(s)!'.format(
                               days=self.through.days_until_can_replay)), )
            # redirect to same page
            return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

        return super(QuizView, self).dispatch(request, *args, **kwargs)

    def get(self, request, *args, **kwargs):
        self.through.make_questions()

        form = QuizForm(self.through)

        if self.through.is_not_running:
            self.through.set_running()

        seconds_left = self.through.time_left

        return render_to_response('quiz/quiz.html',
                                  {'quiz': self.quiz, 'form': form,
                                   'seconds_left': seconds_left},
                                  context_instance=RequestContext(request))

    def post(self, request, **kwargs):
        form = QuizForm(self.through, request.POST)
        results = form.get_response()
        form.check_self_boxes()

        points, gold = self.quiz.calculate_reward(results)
        self.through.set_played(results, points, gold)

        grade = float(points) / self.quiz.points_reward * 10

        return render_to_response('quiz/result.html',
                                  {'quiz': self.quiz,
                                   'points': points,
                                   'grade': grade},
                                  context_instance=RequestContext(request))


quiz = login_required(QuizView.as_view())


def sidebar_widget(context):
    user = context.get('user', None)
    if not user or not user.is_authenticated():
        return ''

    if QuizGame.disabled():
        return ''

    number_of_active_quizzes = Quiz.objects.filter(status='A', type='P').count()

    return render_to_string('quiz/sidebar.html',
                            {'number_of_active_quizzes': number_of_active_quizzes})


register_sidebar_block('quiz', sidebar_widget)
