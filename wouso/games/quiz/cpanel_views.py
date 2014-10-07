from django.views.generic import ListView
from wouso.core.decorators import staff_required
from wouso.games.quiz.models import Quiz

class ListQuizzes(ListView):
    model = Quiz
    paginate_by = 50
    context_object_name = 'quizzes'
    template_name = 'quiz/cpanel/list_quizzes.html'
    
    # def get_queryset(self):
    #     return self.model.objects.all().order_by('-date')

list_quizzes = staff_required(ListQuizzes.as_view())
