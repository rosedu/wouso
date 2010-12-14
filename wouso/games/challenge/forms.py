from django import forms
        

class QuestionForm(forms.Form):
    def __init__(self, question, data=None):
        super(QuestionForm, self).__init__(data)
        self.fields['answers_%d' % question.id] = forms.MultipleChoiceField(widget=forms.CheckboxSelectMultiple,label='')
        self.fields['answers_%d' % question.id].choices = [(a.id, a.text) for a in question.answers()]
        self.question = question
        self.points = 0
        self.all = 0
        self.checked = 0 
        self.missed = 0
        # If data != None, check answer
        if data != None:
            for a in question.answers():
                user_answers = data.getlist('answers_%d' % question.id)
                if unicode(a.id) in user_answers:
                    if a.value: self.checked += 1
                    else: self.missed +=1
                else:
                    if a.value: self.missed += 1
                    else: self.checked += 1
            self.all = self.checked + self.missed
            self.points = float(self.checked) / float(self.all)
            
    def get_result(self):
        return {'points': self.points, 'checked': self.checked, 'missed': self.missed}
                    
    def get_value(self):
        return self.points
                

def challenge_form(challenge, data=None):
    """ Returns a list of forms """
    forms = []
    results = []
    points = 0
    for q in challenge.questions.all():
        form = QuestionForm(q, data)
        forms.append(form)
        if not data == None:
            results.append(form.get_result())
        points += form.get_value()
        
    return {'forms': forms, 'points': points, 'results': results }
