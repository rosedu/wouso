from django import forms

""" Form for data validation """


class QotdForm(forms.Form):
    def __init__(self, qotd, data=None):
        super(QotdForm, self).__init__(data)
        data = [[a.id, a] for a in qotd.answers]
        self.fields['answers'].choices = data

    answers = forms.ChoiceField(widget=forms.RadioSelect(),
                                choices=[])
