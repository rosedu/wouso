from django.contrib.auth.decorators import permission_required
from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from django.core.urlresolvers import reverse_lazy

from wouso.games.quiz.forms import AddQuizForm
from wouso.core.decorators import staff_required
from wouso.games.quiz.models import Quiz


class ListQuizzes(ListView):
    model = Quiz
    paginate_by = 50
    context_object_name = 'quizzes'
    template_name = 'quiz/cpanel/list_quizzes.html'


list_quizzes = staff_required(ListQuizzes.as_view())


class AddQuizView(CreateView):
    form_class = AddQuizForm
    success_url = reverse_lazy('list_quizzes')
    template_name = 'quiz/cpanel/quiz.html'


add_quiz = permission_required('config.change_setting')(
    AddQuizView.as_view())


class EditQuizView(UpdateView):
    model = Quiz
    form_class = AddQuizForm
    success_url = reverse_lazy('list_quizzes')
    template_name = 'quiz/cpanel/quiz.html'


edit_quiz = permission_required('config.change_setting')(EditQuizView.as_view())


class DeleteQuizView(DeleteView):
    model = Quiz
    success_url = reverse_lazy('list_quizzes')

    def get(self, *args, **kwargs):
        return self.delete(*args, **kwargs)


delete_quiz = permission_required('config.change_setting')(
    DeleteQuizView.as_view())
