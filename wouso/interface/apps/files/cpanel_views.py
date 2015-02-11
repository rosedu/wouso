from django.contrib.auth.decorators import permission_required
from django.core.urlresolvers import reverse_lazy
from django.views.generic import ListView, CreateView, UpdateView, DeleteView

from core.decorators import staff_required
from interface.apps.files.forms import FileForm, CategoryForm
from interface.apps.files.models import File, FileCategory


class FilesView(ListView):
    model = File
    paginate_by = 20
    context_object_name = 'files'
    template_name = 'files/cpanel/list_files.html'


files = staff_required(FilesView.as_view())


class AddFileView(CreateView):
    form_class = FileForm
    success_url = reverse_lazy('files')
    template_name = 'files/cpanel/add_file.html'


add_file = permission_required('config.change_setting')(
    AddFileView.as_view())


class EditFileView(UpdateView):
    model = File
    form_class = FileForm
    success_url = reverse_lazy('files')
    template_name = 'files/cpanel/edit_file.html'


edit_file = permission_required('config.change_setting')(
    EditFileView.as_view())


class DeleteFileView(DeleteView):
    model = File
    success_url = reverse_lazy('files')

    def get(self, *args, **kwargs):
        return self.delete(*args, **kwargs)


delete_file = permission_required('config.change_setting')(
    DeleteFileView.as_view())


class ManageCategoriesView(ListView):
    model = FileCategory
    context_object_name = 'categories'
    template_name = 'files/cpanel/manage_categories.html'


manage_categories = permission_required('config.change_setting')(
    ManageCategoriesView.as_view())


class AddCategoryView(CreateView):
    form_class = CategoryForm
    success_url = reverse_lazy('manage_file_categories')
    template_name = 'files/cpanel/category.html'


add_category = permission_required('config.change_setting')(
    AddCategoryView.as_view())


class EditCategoryView(UpdateView):
    model = FileCategory
    form_class = CategoryForm
    success_url = reverse_lazy('manage_file_categories')
    template_name = 'files/cpanel/category.html'


edit_category = permission_required('config.change_setting')(
    EditCategoryView.as_view())


class DeleteCategoryView(DeleteView):
    model = FileCategory
    success_url = reverse_lazy('manage_file_categories')

    def get(self, *args, **kwargs):
        return self.delete(*args, **kwargs)


delete_category = permission_required('config.change_setting')(
    DeleteCategoryView.as_view())
