import re

from django.contrib.auth.decorators import login_required
from django.shortcuts import render_to_response, get_object_or_404
from django.template import RequestContext
from django.template.loader import render_to_string
from django.views.generic import View

from wouso.core.ui import register_sidebar_block
from django.views.generic import TemplateView, ListView
from games.quiz.models import QuizUser, UserToQuiz
from models import Lesson, LessonCategory, LessonTag


class LessonIndexView(ListView):
    """Shows all categories"""
    model = LessonCategory
    context_object_name = 'categories'
    template_name = 'lesson/index.html'


index = login_required(LessonIndexView.as_view())


class LessonCategoryView(ListView):
    """ Shows all tags related to the current category"""
    model = LessonCategory
    context_object_name = 'category'
    template_name = 'lesson/category.html'

    def get_queryset(self):
        return LessonCategory.objects.get(id=self.kwargs['id'])


category = login_required(LessonCategoryView.as_view())


class LessonTagView(ListView):
    """ Shows all lessons related to the current category"""
    model = LessonTag
    context_object_name = 'tag'
    template_name = 'lesson/tag.html'

    def get_queryset(self):
        return LessonTag.objects.get(id=self.kwargs['id'])


tag = login_required(LessonTagView.as_view())


class LessonView(View):
    def dispatch(self, request, *args, **kwargs):
        profile = request.user.get_profile()
        self.quiz_user = profile.get_extension(QuizUser)
        self.lesson = get_object_or_404(Lesson, pk=kwargs['id'])

        try:
            self.through = UserToQuiz.objects.get(user=self.quiz_user, quiz=self.lesson.quiz)
        except UserToQuiz.DoesNotExist:
            if self.lesson.quiz is not None:
                self.through = UserToQuiz(user=self.quiz_user, quiz=self.lesson.quiz)
                self.through.save()

        return super(LessonView, self).dispatch(request, *args, **kwargs)

    def get(self, request, *args, **kwargs):
        if not hasattr(self, 'through'):
            self.through = None

        # get YouTube embed video url
        match = re.search(r'^(http|https)\:\/\/www\.youtube\.com\/watch\?v\=(\w*)(\&(.*))?$', self.lesson.youtube_url)
        if match:
            embed_url = '//www.youtube.com/embed/%s' % (match.group(2))
        else:
            embed_url = ''

        return render_to_response('lesson/lesson.html',
                                  {'lesson': self.lesson, 'through': self.through,
                                   'embed_url': embed_url},
                                  context_instance=RequestContext(request))


lesson = login_required(LessonView.as_view())


def sidebar_widget(context):
    user = context.get('user', None)
    if not user or not user.is_authenticated():
        return ''

    if Lesson.disabled():
        return ''

    return render_to_string('lesson/sidebar.html', {})


register_sidebar_block('lesson', sidebar_widget)
