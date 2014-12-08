from django.views.generic import ListView, DetailView, CreateView
from django.contrib.auth.decorators import login_required

from models import Category, Forum, Topic
from forms import TopicCreateForm


class CategoryView(ListView):
    model = Category
    template_name = 'forum/categories.html'


category = login_required(CategoryView.as_view())


class ForumView(DetailView):
    model = Forum
    template_name = 'forum/forum.html'


forum = login_required(ForumView.as_view())


class TopicView(DetailView):
    model = Topic
    template_name = 'forum/topic.html'


topic = login_required(TopicView.as_view())


class TopicCreateView(CreateView):
    model = Topic
    template_name = 'forum/topic_create.html'
    form_class = TopicCreateForm


topic_create = login_required(TopicCreateView.as_view())
