from django.contrib.auth.decorators import permission_required
from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from django.core.urlresolvers import reverse_lazy

from wouso.games.quiz.forms import AddQuizForm, CategoryForm
from wouso.core.decorators import staff_required
from wouso.games.quiz.models import Quiz, QuizCategory


class ListQuizzes(ListView):
    model = Quiz
    paginate_by = 20
    context_object_name = 'quizzes'
    template_name = 'quiz/cpanel/list_quizzes.html'


list_quizzes = staff_required(ListQuizzes.as_view())


class AddQuizView(CreateView):
    form_class = AddQuizForm
    success_url = reverse_lazy('list_quizzes')
    template_name = 'quiz/cpanel/add_quiz.html'


add_quiz = permission_required('config.change_setting')(
    AddQuizView.as_view())


class EditQuizView(UpdateView):
    model = Quiz
    form_class = AddQuizForm
    success_url = reverse_lazy('list_quizzes')
    template_name = 'quiz/cpanel/add_quiz.html'


edit_quiz = permission_required('config.change_setting')(
    EditQuizView.as_view())


class DeleteQuizView(DeleteView):
    model = Quiz
    success_url = reverse_lazy('list_quizzes')

    def get(self, *args, **kwargs):
        return self.delete(*args, **kwargs)


delete_quiz = permission_required('config.change_setting')(
    DeleteQuizView.as_view())


class ManageCategoriesView(ListView):
    model = QuizCategory
    context_object_name = 'categories'
    template_name = 'quiz/cpanel/manage_categories.html'


manage_categories = permission_required('config.change_setting')(
    ManageCategoriesView.as_view())


class AddCategoryView(CreateView):
    form_class = CategoryForm
    success_url = reverse_lazy('manage_quiz_categories')
    template_name = 'quiz/cpanel/category.html'


add_category = permission_required('config.change_setting')(
    AddCategoryView.as_view())


class EditCategoryView(UpdateView):
    model = QuizCategory
    form_class = CategoryForm
    success_url = reverse_lazy('manage_quiz_categories')
    template_name = 'quiz/cpanel/category.html'


edit_category = permission_required('config.change_setting')(
    EditCategoryView.as_view())


class DeleteCategoryView(DeleteView):
    model = QuizCategory
    success_url = reverse_lazy('manage_quiz_categories')

    def get(self, *args, **kwargs):
        return self.delete(*args, **kwargs)


delete_category = permission_required('config.change_setting')(
    DeleteCategoryView.as_view())
