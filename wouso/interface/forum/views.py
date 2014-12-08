from django.views.generic import ListView, DetailView
from django.contrib.auth.decorators import login_required

from wouso.interface.forum.models import Category, Forum, Topic


class CategoryView(ListView):
    model = Category
    template_name = 'forum/category_list.html'
    context_object_name = 'category_list'

    print Category.objects.all()


category = login_required(CategoryView.as_view())


class ForumView(DetailView):
    model = Forum


forum = login_required(ForumView.as_view())


class TopicView(DetailView):
    model = Topic


topic = login_required(TopicView.as_view())
