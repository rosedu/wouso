from django import forms
from wouso.core.qpool.models import Question, Answer, Schedule, Category

class QuestionForm(forms.Form):
    text = forms.CharField(max_length=500, widget=forms.Textarea)
    active = forms.BooleanField(required=False)
    schedule = forms.DateField(required=False)
    category = forms.CharField(max_length=50, required=False)

    def __init__(self, data=None, instance=None):
        super(QuestionForm, self).__init__(data)
        if data is not None:
            for i in filter(lambda a: a.startswith('answer_'), data.keys()):
                i = int(i[7:])
                self.fields['answer_%d' % i] = forms.CharField(max_length=100,
                                        widget=forms.Textarea, required=False)
                self.fields['correct_%d' % i] = forms.BooleanField(required=False)

        self.instance = instance

    def save(self):
        data = self.cleaned_data
        if self.instance is None:
            new = True
            self.instance = Question.objects.create()
            self.instance.category, nn = Category.objects.get_or_create(name=data['category'])
            self.instance.save()
        else:
            new = False

        for i in filter(lambda a: a.startswith('answer_'), data.keys()):
            i = int(i[7:])
            if not new:
                a = Answer.objects.get(pk=i)
            else:
                if not data['answer_%d' % i]:
                    continue
                a = Answer.objects.create(question=self.instance)
            a.text = data['answer_%d' % i]
            a.correct = data['correct_%d' % i]
            a.save()

        self.instance.text = data['text']
        self.instance.active = data['active']
        # for qotd, scheduled
        if self.instance.category.name == 'qotd':
            sched = Schedule.objects.filter(question=self.instance)
            if sched:
                sched = sched[0]
            else:
                sched = Schedule.objects.create(question=self.instance)
            if data['schedule'] is None:
                sched.delete()
            else:
                sched.day = data['schedule']
                sched.save()
        self.instance.save()
