from django import forms
from django.core.urlresolvers import reverse
from django.shortcuts import redirect
from django.views.generic import TemplateView, ListView, DetailView, UpdateView
from models import SpecialChallenge


class StatusUpdate(forms.ModelForm):
    class Meta:
        model = SpecialChallenge
        fields = ('status',)


class CpanelHome(ListView):
    template_name = 'specialchallenge/cpanel/home.html'
    model = SpecialChallenge


class CpanelChallenge(UpdateView):
    template_name = 'specialchallenge/cpanel/challenge.html'
    model = SpecialChallenge
    form_class = StatusUpdate

    def form_valid(self, form):
        self.object = form.save()
        # create a challenge
        self.object.update_challenge()
        return redirect(self.get_success_url())

    def get_success_url(self):
        return reverse('sc_home')