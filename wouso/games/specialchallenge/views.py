# Django 1.3 from now on
from django.core.urlresolvers import reverse
from django.shortcuts import redirect, get_object_or_404
from django.views.generic import TemplateView, FormView, DetailView, UpdateView, DeleteView
from forms import CreateForm, QuestionForm, ConfigureForm
from models import SpecialChallenge, SpecialChallengeGame
from wouso.core.qpool.models import Question


class IndexView(TemplateView):
    template_name = 'specialchallenge/index.html'


class CreateChallenge(FormView):
    template_name = 'specialchallenge/create.html'
    form_class = CreateForm

    def form_valid(self, form):
        # TODO: create a widget using the player_input template tag
        player_to = form.cleaned_data['player_to']
        player_from = self.request.user.get_profile()
        chal = SpecialChallenge.create(player_from, player_to)
        return redirect('specialchallenge_configure', challenge=chal.id)


class ConfigureChallenge(UpdateView):
    template_name = 'specialchallenge/configure.html'
    model = SpecialChallenge
    form_class = ConfigureForm

    def form_valid(self, form):
        chal = form.save()
        return redirect('specialchallenge_add_question', challenge=chal.id)


class ChallengeMixin(object):
    def get_context_data(self, **kwargs):
        context = super(ChallengeMixin, self).get_context_data(**kwargs)
        challenge = get_object_or_404(SpecialChallenge, pk=self.kwargs['challenge'])
        self.challenge = challenge
        context.update({'challenge': self.challenge})
        return context


class ChallengeQuestionAdd(ChallengeMixin, FormView):
    template_name = 'specialchallenge/challenge_add_question.html'
    form_class = QuestionForm

    def form_valid(self, form):
        question = form.save()
        question.proposed_by = self.request.user
        question.category = SpecialChallengeGame.get_category()
        question.save()
        self.get_context_data()
        self.challenge.questions.add(question)
        return redirect('specialchallenge_challenge', pk=self.challenge.id)


class ChallengeQuestionEdit(ChallengeMixin, UpdateView):
    template_name = 'specialchallenge/challenge_edit_question.html'
    form_class = QuestionForm
    model = Question

    def get_success_url(self):
        self.get_context_data()
        return reverse('specialchallenge_challenge', args=(self.challenge.id,))


class ChallengeQuestionDelete(ChallengeMixin, DeleteView):
    template_name = 'specialchallenge/challenge_del_question.html'
    model = Question

    def get_success_url(self):
        self.get_context_data()
        return reverse('specialchallenge_challenge', args=(self.challenge.id,))


class ChallengeView(DetailView):
    template_name = 'specialchallenge/challenge_view.html'
    model = SpecialChallenge
    context_object_name = 'challenge'
