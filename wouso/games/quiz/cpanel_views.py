from django.contrib.auth.decorators import permission_required
from django.views.generic import ListView, CreateView
from django.core.urlresolvers import reverse_lazy

from games.quiz.forms import QuizForm
from wouso.core.decorators import staff_required
from wouso.games.quiz.models import Quiz


class ListQuizzes(ListView):
    model = Quiz
    paginate_by = 50
    context_object_name = 'quizzes'
    template_name = 'quiz/cpanel/list_quizzes.html'
    
    # def get_queryset(self):
    #     return self.model.objects.all().order_by('-date')

list_quizzes = staff_required(ListQuizzes.as_view())


class AddQuizView(CreateView):
    template_name = 'quiz/cpanel/add_quiz.html'
    form_class = QuizForm
    success_url = reverse_lazy('list_quizzes')


add_quiz = permission_required('config.change_setting')(
    AddQuizView.as_view())
