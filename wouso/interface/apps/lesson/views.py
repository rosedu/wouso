from django.utils.translation import ugettext as _
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import render_to_response, get_object_or_404
from django.template import RequestContext
from django.template.loader import render_to_string
from django.views.generic import View

from wouso.core.ui import register_sidebar_block
from games.quiz.forms import QuizForm
from games.quiz.models import QuizUser, UserToQuiz
from models import Lesson, LessonCategory


@login_required
def index(request):
    """ Shows all lesson related to the current user """
    categories = LessonCategory.objects.all()
    return render_to_response('lesson/index.html',
                              {'categories':categories},
                              context_instance=RequestContext(request))


class LessonView(View):
    def dispatch(self, request, *args, **kwargs):
        profile = request.user.get_profile()
        self.quiz_user = profile.get_extension(QuizUser)
        self.lesson = get_object_or_404(Lesson, pk=kwargs['id'])

        try:
            self.through = UserToQuiz.objects.get(user=self.quiz_user, quiz=self.lesson.quiz)
        except UserToQuiz.DoesNotExist:
            self.through = UserToQuiz(user=self.quiz_user, quiz=self.lesson.quiz)
            self.through.save()

        # check if user is eligible to play quiz
        if not self.through.can_play_again():
            messages.error(request, _('You have already submitted this quiz!'))

        return super(LessonView, self).dispatch(request, *args, **kwargs)

    def get(self, request, *args, **kwargs):
        self.through.make_questions()
        form = QuizForm(self.through)

        if self.through.is_not_running():
            self.through.set_running()

        seconds_left = self.through.time_left

        return render_to_response('lesson/lesson.html',
                                  {'lesson': self.lesson,
                                   'form': form, 'seconds_left': seconds_left},
                                  context_instance=RequestContext(request))


lesson = login_required(LessonView.as_view())


def sidebar_widget(context):
    user = context.get('user', None)
    if not user or not user.is_authenticated():
        return ''

    return render_to_string('lesson/sidebar.html', {})


register_sidebar_block('lesson', sidebar_widget)
