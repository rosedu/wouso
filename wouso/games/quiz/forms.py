from random import shuffle
from django import forms
from core.qpool import get_questions_with_tag_and_category
from games.quiz.models import QuizException
from wouso.games.quiz.models import Quiz


class QuizForm(forms.Form):
    def __init__(self, quiz, data=None):
        super(QuizForm, self).__init__(data)

        for q in quiz.questions.all():
            field = forms.MultipleChoiceField(
                widget=forms.CheckboxSelectMultiple,
                label=q.text)
            field.choices = [(a.id, a.text) for a in q.shuffled_answers]
            self.fields['answer_{id}'.format(id=q.id)] = field
        self.data = data

    def get_response(self):
        """ Parse response and return comprehensive list of ids """
        res = {}
        for f in filter(lambda name: name.startswith('answer_'), self.data):
            id = int(f[len('answer_'):])
            res[id] = [int(i) for i in self.data.getlist(f)]

        """ Checking if a question has no selected answers and
        adding an empty list to dic in this case"""
        for field in self.visible_fields():
            id = int(field.html_name[len('answer_'):])
            if not res.has_key(id):
                res[id] = []
        return res

    def check_self_boxes(self):
        for i in range(len(self.visible_fields())):
            field = self.visible_fields()[i]
            checked_boxes = self.data.getlist(field.html_name)
            for j in range(len(field.field.choices)):
                choice = field.field.choices[j]
                if str(choice[0]) in checked_boxes:
                    self.visible_fields()[i].field.choices[j] = (choice[0], choice[1], True)

    def get_results_in_order(self, results):
        """ Assign question feedback with according question """
        v = []
        for field in self.visible_fields():
            id = int(field.html_name[len('answer_'):])
            v.append(results[id])
        return v


class AddQuizForm(forms.ModelForm):
    tag = forms.CharField()

    class Meta:
        model = Quiz
        exclude = ['questions', 'owner', 'players']

    def save(self):
        data = self.cleaned_data

        questions = [q for q in get_questions_with_tag_and_category(data['tag'], 'quiz')]
        if len(questions) < data['number_of_questions']:
            raise QuizException('Too few questions')
        shuffle(questions)
        questions_qs = questions[:data['number_of_questions']]

        self.instance.save()
        self.instance.questions = questions_qs

        return self.instance
