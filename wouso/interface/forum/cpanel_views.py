from django.contrib.auth.decorators import permission_required
from django.core.urlresolvers import reverse_lazy, reverse
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404, redirect
from django.views.generic import ListView, CreateView, UpdateView, DeleteView

from core.decorators import staff_required
from interface.forum.models import Forum, Category
from interface.forum.forms import CategoryForm, ForumForm


class ForumIndexView(ListView):
    model = Forum
    context_object_name = 'forums'
    template_name = 'forum/cpanel/index.html'

    def get_context_data(self, **kwargs):
        context = super(ForumIndexView, self).get_context_data(**kwargs)
        context['categories'] = Category.objects.all()
        return context


forum = staff_required(ForumIndexView.as_view())


class AddForumView(CreateView):
    form_class = ForumForm
    success_url = reverse_lazy('forum')
    template_name = 'forum/cpanel/add_forum.html'


add_forum = permission_required('config.change_setting')(
    AddForumView.as_view())


class EditForumView(UpdateView):
    model = Forum
    form_class = ForumForm
    success_url = reverse_lazy('forum')
    template_name = 'forum/cpanel/edit_forum.html'


edit_forum = permission_required('config.change_setting')(
    EditForumView.as_view())


class DeleteForumView(DeleteView):
    model = Forum
    success_url = reverse_lazy('forum')

    def get(self, *args, **kwargs):
        return self.delete(*args, **kwargs)


delete_forum = permission_required('config.change_setting')(
    DeleteForumView.as_view())


class ManageForumCategoriesView(ListView):
    model = Category
    context_object_name = 'categories'
    template_name = 'forum/cpanel/manage_categories.html'


manage_forum_categories = permission_required('config.change_setting')(
    ManageForumCategoriesView.as_view())


class AddForumCategoryView(CreateView):
    form_class = CategoryForm
    success_url = reverse_lazy('manage_forum_categories')
    template_name = 'forum/cpanel/add_category.html'


add_forum_category = permission_required('config.change_setting')(
    AddForumCategoryView.as_view())


class EditForumCategoryView(UpdateView):
    model = Category
    form_class = CategoryForm
    success_url = reverse_lazy('manage_forum_categories')
    template_name = 'forum/cpanel/edit_category.html'


edit_forum_category = permission_required('config.change_setting')(
    EditForumCategoryView.as_view())


class DeleteForumCategoryView(DeleteView):
    model = Category
    success_url = reverse_lazy('manage_forum_categories')

    def get(self, *args, **kwargs):
        return self.delete(*args, **kwargs)


delete_forum_category = permission_required('config.change_setting')(
    DeleteForumCategoryView.as_view())


@permission_required('config.change_setting')
def forum_switch_closed(request, id):
    forum = get_object_or_404(Forum, pk=id)

    forum.is_closed = not forum.is_closed
    forum.save()

    return HttpResponseRedirect(reverse('forum'))


@permission_required('config.change_setting')
def forum_actions(request):
    action = request.GET.get('action', None)
    f_id = request.GET.get('f_id', '').split()
    f_id = map(int, f_id)
    queryset = Forum.objects.filter(id__in=f_id)

    if action == 'closed':
        for f in queryset:
            f.is_closed = True
            f.save()
    elif action == 'open':
        for f in queryset:
            f.is_closed = False
            f.save()

    redir = request.META.get('HTTP_REFERER', reverse('forum'))

    return redirect(redir)
