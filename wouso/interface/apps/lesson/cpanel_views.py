from django.contrib.auth.decorators import permission_required
from django.core.urlresolvers import reverse_lazy, reverse
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404, render_to_response, redirect
from django.template import RequestContext
from django.views.generic import ListView, CreateView, UpdateView, DeleteView, FormView

from core.decorators import staff_required
from interface.apps.lesson.forms import CategoryForm, TagForm, AddLessonForm, EditLessonForm
from interface.apps.lesson.models import Lesson, LessonCategory, LessonTag
from games.quiz.models import Quiz


class LessonsView(ListView):
    model = Lesson
    paginate_by = 20
    context_object_name = 'lessons'
    template_name = 'lesson/cpanel/list_lessons.html'

    def get_context_data(self, **kwargs):
        context = super(LessonsView, self).get_context_data(**kwargs)
        context['categories'] = LessonCategory.objects.all()
        return context


lessons = staff_required(LessonsView.as_view())


class AddLessonView(FormView):
    form_class = AddLessonForm
    template_name = 'lesson/cpanel/add_lesson.html'

    def get_form_kwargs(self):
        return dict(data=self.request.POST)

    def form_valid(self, form):
        form.save()
        return redirect('lessons')

    def get_context_data(self, **kwargs):
        context = super(AddLessonView, self).get_context_data(**kwargs)
        categories = [(c.name.capitalize(), c.name) for c in LessonCategory.objects.all()]
        context['categories'] = categories
        return context


add_lesson = permission_required('config.change_setting')(
    AddLessonView.as_view())


@permission_required('config.change_setting')
def edit_lesson(request, id):
    lesson = get_object_or_404(Lesson, pk=id)
    categories = [(c.name, c.name.capitalize()) for c in LessonCategory.objects.all()]
    lesson_quizzes = Quiz.objects.filter(type='L')

    if request.method == 'POST':
        form = EditLessonForm(request.POST, instance=lesson)
        if form.is_valid():
            new_lesson = form.save()
            return redirect('lessons')
    else:
        form = EditLessonForm(instance=lesson)

    return render_to_response('lesson/cpanel/edit_lesson.html',
                              {'lesson': lesson, 'form': form, 'categories': categories,
                               'lesson_quizzes': lesson_quizzes},
                              context_instance=RequestContext(request))


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
    success_url = reverse_lazy('manage_lesson_categories')
    template_name = 'lesson/cpanel/category.html'


add_category = permission_required('config.change_setting')(
    AddCategoryView.as_view())


class EditCategoryView(UpdateView):
    model = LessonCategory
    form_class = CategoryForm
    success_url = reverse_lazy('manage_lesson_categories')
    template_name = 'lesson/cpanel/category.html'


edit_category = permission_required('config.change_setting')(
    EditCategoryView.as_view())


class DeleteCategoryView(DeleteView):
    model = LessonCategory
    success_url = reverse_lazy('manage_lesson_categories')

    def get(self, *args, **kwargs):
        return self.delete(*args, **kwargs)


delete_category = permission_required('config.change_setting')(
    DeleteCategoryView.as_view())


class ManageTagsView(ListView):
    model = LessonTag
    context_object_name = 'tags'
    template_name = 'lesson/cpanel/manage_tags.html'


manage_tags = permission_required('config.change_setting')(
    ManageTagsView.as_view())


class AddTagView(CreateView):
    form_class = TagForm
    success_url = reverse_lazy('manage_lesson_tags')
    template_name = 'lesson/cpanel/tag.html'


add_tag = permission_required('config.change_setting')(
    AddTagView.as_view())


class EditTagView(UpdateView):
    model = LessonTag
    form_class = TagForm
    success_url = reverse_lazy('manage_lesson_tags')
    template_name = 'lesson/cpanel/tag.html'


edit_tag = permission_required('config.change_setting')(
    EditTagView.as_view())


class DeleteTagView(DeleteView):
    model = LessonTag
    success_url = reverse_lazy('manage_lesson_tags')

    def get(self, *args, **kwargs):
        return self.delete(*args, **kwargs)


delete_tag = permission_required('config.change_setting')(
    DeleteTagView.as_view())


@permission_required('config.change_setting')
def sort_lessons(request, id):
    tag = get_object_or_404(LessonTag, pk=id)

    if request.method == 'POST':
        new_order = request.POST.get('order')
        if new_order:
            order = [i[1] for i in map(lambda a: a.split('='), new_order.split('&'))]
            tag.set_order(order)
            return HttpResponseRedirect(reverse('manage_lesson_tags'))

    return render_to_response('lesson/cpanel/sort_lessons.html',
                              {'tag': tag, 'module': 'tag'},
                              context_instance=RequestContext(request))


@permission_required('config.change_setting')
def sort_tags(request, id):
    category = get_object_or_404(LessonCategory, pk=id)

    if request.method == 'POST':
        new_order = request.POST.get('order')
        if new_order:
            order = [i[1] for i in map(lambda a: a.split('='), new_order.split('&'))]
            category.set_order(order)
            return HttpResponseRedirect(reverse('manage_lesson_categories'))

    return render_to_response('lesson/cpanel/sort_tags.html',
                              {'category': category, 'module': 'category'},
                              context_instance=RequestContext(request))


@permission_required('config.change_setting')
def lesson_switch_active(request, id):
    lesson = get_object_or_404(Lesson, pk=id)

    lesson.active = not lesson.active
    lesson.save()

    return HttpResponseRedirect(reverse('lessons'))


@permission_required('config.change_setting')
def lesson_actions(request):
    action = request.GET.get('action', None)
    l_id = request.GET.get('l_id', '').split()
    l_id = map(int, l_id)
    queryset = Lesson.objects.filter(id__in=l_id)

    if action == 'active':
        for l in queryset:
            l.active = True
            l.save()
    elif action == 'inactive':
        for l in queryset:
            l.active = False
            l.save()

    redir = request.META.get('HTTP_REFERER', reverse('lessons'))

    return redirect(redir)
