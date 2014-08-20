from django.contrib.auth.decorators import permission_required
from django.views.generic import UpdateView, CreateView, ListView
from django.core.urlresolvers import reverse, reverse_lazy
from django.shortcuts import get_object_or_404
from django.http import HttpResponseRedirect
from wouso.core.decorators import staff_required
from wouso.interface.cpanel.forms import StaticPageForm, NewsForm
from wouso.interface.apps.pages.models import StaticPage, NewsItem
from wouso.interface.cpanel.views import ModuleViewMixin


class StaticPagesView(ModuleViewMixin, ListView):
    template_name = 'cpanel/static_pages.html'
    model = StaticPage

    def get_context_data(self, **kwargs):
        context = super(StaticPagesView, self).get_context_data(**kwargs)
        context['pages'] = StaticPage.objects.all()
        return context


static_pages = staff_required(StaticPagesView.as_view())


class AddStaticPageView(CreateView):
    template_name = 'cpanel/add_static_page.html'
    model = StaticPage
    form_class = StaticPageForm
    success_url = reverse_lazy('static_pages')


add_static_page = permission_required('config.change_setting')(
    AddStaticPageView.as_view())


class EditStaticPageView(UpdateView):
    template_name = 'cpanel/edit_static_page.html'
    model = StaticPage
    form_class = StaticPageForm
    success_url = reverse_lazy('static_pages')


edit_static_page = permission_required('config.change_setting')(
    EditStaticPageView.as_view())


@permission_required('config.change_setting')
def del_static_page(request, pk):
    page = get_object_or_404(StaticPage, pk=pk)

    page.delete()

    go_back = request.META.get('HTTP_REFERER', None)
    if not go_back:
        go_back = reverse('wouso.interface.cpanel.views.static_pages')

    return HttpResponseRedirect(go_back)


class NewsView(ModuleViewMixin, ListView):
    template_name = 'cpanel/news.html'
    model = NewsItem
    context_object_name = 'news'


news = permission_required('config.change_setting')(NewsView.as_view())


class AddNewsView(CreateView):
    template_name = "cpanel/add_news.html"
    model = NewsItem
    form_class = NewsForm

    def get_success_url(self):
        return reverse('news')


add_news = permission_required('config.change_setting')(
    AddNewsView.as_view())


class EditNewsView(UpdateView):
    template_name = "cpanel/edit_news.html"
    model = NewsItem
    form_class = NewsForm
    success_url = reverse_lazy('news')


edit_news = permission_required('config.change_setting')(
    EditNewsView.as_view())


@permission_required('config.change_setting')
def del_news(request, pk):
    news_item = get_object_or_404(NewsItem, pk=pk)

    news_item.delete()

    go_back = request.META.get('HTTP_REFERER', None)
    if not go_back:
        go_back = reverse('wouso.interface.cpanel.views.news')

    return HttpResponseRedirect(go_back)
