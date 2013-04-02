from django.views.generic import ListView
from wouso.core.decorators import staff_required
from wouso.games.challenge.models import Challenge

class ListChallenges(ListView):
    model = Challenge
    paginate_by = 50
    context_object_name = 'challenges'
    template_name = 'challenge/cpanel/list_challenges.html'
    
    def get_queryset(self):
        return self.model.objects.all().order_by('-date')

list_challenges = staff_required(ListChallenges.as_view())
