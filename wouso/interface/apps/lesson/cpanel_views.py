from django.contrib.auth.decorators import permission_required
from django.core.urlresolvers import reverse_lazy
from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from core.decorators import staff_required
from interface.apps.lesson.forms import LessonForm, CategoryForm
from interface.apps.lesson.models import Lesson, LessonCategory


class LessonsView(ListView):
    model = Lesson
    paginate_by = 50
    context_object_name = 'lessons'
    template_name = 'lesson/cpanel/list_lessons.html'


lessons = staff_required(LessonsView.as_view())


class AddLessonView(CreateView):
    form_class = LessonForm
    success_url = reverse_lazy('lessons')
    template_name = 'lesson/cpanel/add_lesson.html'


add_lesson = permission_required('config.change_setting')(
    AddLessonView.as_view())


class EditLessonView(UpdateView):
    model = Lesson
    form_class = LessonForm
    success_url = reverse_lazy('lessons')
    template_name = 'lesson/cpanel/edit_lesson.html'


edit_lesson = permission_required('config.change_setting')(
    EditLessonView.as_view())


class DeleteLessonView(DeleteView):
    model = Lesson
    success_url = reverse_lazy('lessons')

    def get(self, *args, **kwargs):
        return self.delete(*args, **kwargs)


delete_lesson = permission_required('config.change_setting')(
    DeleteLessonView.as_view())


class ManageCategoriesView(ListView):
    model = LessonCategory
    context_object_name = 'categories'
    template_name = 'lesson/cpanel/manage_categories.html'


manage_categories = permission_required('config.change_setting')(
    ManageCategoriesView.as_view())


class AddCategoryView(CreateView):
    form_class = CategoryForm
    success_url = reverse_lazy('manage_categories')
    template_name = 'lesson/cpanel/category.html'


add_category = permission_required('config.change_setting')(
    AddCategoryView.as_view())


class EditCategoryView(UpdateView):
    model = LessonCategory
    form_class = CategoryForm
    success_url = reverse_lazy('manage_categories')
    template_name = 'lesson/cpanel/category.html'


edit_category = permission_required('config.change_setting')(
    EditCategoryView.as_view())


class DeleteCategoryView(DeleteView):
    model = LessonCategory
    success_url = reverse_lazy('manage_categories')

    def get(self, *args, **kwargs):
        return self.delete(*args, **kwargs)


delete_category = permission_required('config.change_setting')(
    DeleteCategoryView.as_view())
