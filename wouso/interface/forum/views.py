from django.contrib import messages
from django.http import HttpResponseRedirect
from django.views.generic import ListView, DetailView, FormView
from django.core.urlresolvers import reverse, reverse_lazy
from django.contrib.auth.decorators import login_required

from wouso.interface.forum.models import Category, Forum, Topic, Post, ForumUser
from wouso.interface.forum.forms import TopicCreateForm, PostCreateForm


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


class TopicCreateView(FormView):
    template_name = 'forum/topic_create.html'
    form_class = TopicCreateForm

    def dispatch(self, request, *args, **kwargs):
        self.forum = Forum.objects.get(id=kwargs.get('forum_id', None))
        if self.forum.is_closed and not request.user.is_staff:
            messages.error(request, "You do not have the permissions to create a topic")
            return HttpResponseRedirect(reverse_lazy('forum', args=[self.forum.id]))

        return super(TopicCreateView, self).dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        data = form.cleaned_data
        profile = self.request.user.get_profile()
        forum_user = profile.get_extension(ForumUser)

        topic = Topic(forum=self.forum, name=data['topic'])
        topic.save()

        post = Post(topic=topic, text=data['text'], user=forum_user)
        post.save()

        topic.last_post = post
        topic.save()

        self.success_url = reverse('topic', args=[topic.id])

        return super(TopicCreateView, self).form_valid(form)

    def get_context_data(self, **kwargs):
        context = super(TopicCreateView, self).get_context_data(**kwargs)
        context['forum'] = Forum.objects.get(id=self.kwargs.get('forum_id', None))
        return context


topic_create = login_required(TopicCreateView.as_view())


class PostCreateView(FormView):
    template_name = 'forum/post_create.html'
    form_class = PostCreateForm

    def dispatch(self, request, *args, **kwargs):
        self.topic = Topic.objects.get(id=kwargs.get('pk', None))
        self.parent_post = Post.objects.get(id=kwargs.get('post_id', None))
        if self.topic.forum.is_closed and not request.user.is_staff:
            messages.error(request, "You do not have the permissions to create a post")
            return HttpResponseRedirect(reverse_lazy('forum', args=[self.topic.forum.id]))

        return super(PostCreateView, self).dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        message = form.cleaned_data['message']
        profile = self.request.user.get_profile()
        forum_user = profile.get_extension(ForumUser)

        post = Post(topic=self.topic, text=message, user=forum_user)
        post.save()
        self.parent_post.replies.add(post)

        post.topic.last_post = post
        post.topic.save()

        self.success_url = reverse('topic', args=[self.topic.id])

        return super(PostCreateView, self).form_valid(form)

    def get_context_data(self, **kwargs):
        context = super(PostCreateView, self).get_context_data(**kwargs)
        context['topic'] = Topic.objects.get(id=self.kwargs.get('pk', None))
        context['post'] = Post.objects.get(id=self.kwargs.get('post_id', None))
        return context


post_create = login_required(PostCreateView.as_view())
