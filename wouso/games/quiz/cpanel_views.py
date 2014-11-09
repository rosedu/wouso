from django.contrib.auth.decorators import permission_required
from django.views.generic import ListView, CreateView, UpdateView
from django.core.urlresolvers import reverse_lazy
from django.shortcuts import get_object_or_404, redirect

from games.quiz.forms import AddQuizForm
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
    form_class = AddQuizForm
    success_url = reverse_lazy('list_quizzes')

add_quiz = permission_required('config.change_setting')(
    AddQuizView.as_view())


@permission_required('config.change_setting')
def delete_quiz(request, id):
    quiz = get_object_or_404(Quiz, pk=id)
    quiz.delete()
    return redirect('list_quizzes')


class EditQuizView(UpdateView):
    template_name = 'quiz/cpanel/edit_quiz.html'
    model = Quiz
    form_class = AddQuizForm
    success_url = reverse_lazy('list_quizzes')

edit_quiz = permission_required('config.change_setting')(EditQuizView.as_view())
