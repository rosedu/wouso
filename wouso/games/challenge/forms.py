from django import forms

class ChallengeForm(forms.Form):
    def __init__(self, challenge, data=None):
        super(ChallengeForm, self).__init__(data)

        for q in challenge.questions.all():
            field = forms.MultipleChoiceField(widget=forms.CheckboxSelectMultiple, label=q)
            field.choices = [(a.id, a) for a in q.shuffled_answers]
            self.fields['answer_{id}'.format(id = q.id)] = field
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
            
            if not id in res:
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