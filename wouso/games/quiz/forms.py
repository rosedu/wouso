from random import shuffle
from datetime import datetime

from django import forms

from core.qpool import get_questions_with_tag_and_category
from core.qpool.models import Tag
from wouso.games.quiz.models import Quiz, QuizCategory

from bootstrap3_datetime import widgets


class QuizForm(forms.Form):
    def __init__(self, through, data=None):
        super(QuizForm, self).__init__(data)

        questions = list(through.questions.all())
        shuffle(questions)

        for q in questions:
            field = forms.MultipleChoiceField(
                widget=forms.CheckboxSelectMultiple,
                label=q)
            field.choices = [(a.id, a) for a in q.shuffled_answers]
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
    tags = forms.ModelMultipleChoiceField(
            queryset=Tag.objects.filter(category__name='quiz'))

    class Meta:
        model = Quiz

        widgets = {'start': widgets.DateTimePicker(options={"format": "YYYY-MM-DD HH:mm:ss"}),
                   'end': widgets.DateTimePicker(options={"format": "YYYY-MM-DD HH:mm:ss"})
        }
        exclude = ['owner', 'players', 'status']

    def __init__(self, *args, **kwargs):
        super(AddQuizForm, self).__init__(*args, **kwargs)

        self.fields['start'].label = "Starts on"
        self.fields['end'].label = "Ends on"
        self.fields['tags'].label = "Question tags"
        self.fields['time_limit'].label = "Time limit (seconds)"
        self.fields['another_chance'].label = "Retake quiz after (days)"

    def save(self, commit=True):
        data = self.cleaned_data

        # Get a list of questions from the Quiz category with tags selected
        # by staff user
        tags_list = [t for t in data['tags']]
        all_questions = [q for q in get_questions_with_tag_and_category(tags_list, 'quiz')]

        self.instance.save()
        self.instance.tags = tags_list

        # If not enough questions in tag(s) set quiz's number of questions
        # as max number of questions available
        if len(all_questions) < data['number_of_questions']:
            self.instance.number_of_questions = len(all_questions)
        else:
            self.instance.number_of_questions = data['number_of_questions']

        self.instance.save()

        # Set status based on current date and time (Active, Inactive, Expired)
        now = datetime.now()
        if data['start'] <= now <= data['end']:
            self.instance.status = 'A'
        elif data['start'] > now:
            self.instance.status = 'I'
        elif data['end'] < now:
            self.instance.status = 'E'
        self.instance.save()

        return self.instance


class CategoryForm(forms.ModelForm):
    class Meta:
        model = QuizCategory
