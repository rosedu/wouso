import pickle
from random import shuffle
from datetime import datetime

from django import forms

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
    class Meta:
        model = Quiz

        widgets = {'start': widgets.DateTimePicker(options={"format": "YYYY-MM-DD HH:mm:ss"}),
                   'end': widgets.DateTimePicker(options={"format": "YYYY-MM-DD HH:mm:ss"})
        }
        exclude = ['owner', 'players', 'status', 'tags']

    def __init__(self, *args, **kwargs):
        super(AddQuizForm, self).__init__(*args, **kwargs)

        self.fields['start'].label = "Starts on"
        self.fields['end'].label = "Ends on"
        self.fields['time_limit'].label = "Time limit (seconds)"
        self.fields['another_chance'].label = "Retake quiz after (days)"

        tags = pickle.loads(self.instance.tags) if self.instance.tags else {}

        for t in Tag.objects.filter(category__name='quiz'):
            initial = tags[t.name] if t.name in tags else 0
            self.fields['tag_%s' % t] = forms.IntegerField(label=unicode(t), initial=initial)

    def save(self, commit=True):
        data = self.cleaned_data

        # Create a dict containing tags as keys and the corresponding number of
        # questions to be taken from the pool as values
        # e.g. {'Tag1': 1, 'Tag2': 2}
        tags = {}
        for k in data:
            v = data[k]
            if k.startswith('tag_'):
                k = k.replace('tag_', '')
                tags[k] = v

        self.instance.save()
        self.instance.tags = pickle.dumps(tags)

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
