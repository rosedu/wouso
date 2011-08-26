from django import forms

class SearchForm(forms.Form):
    query = forms.CharField(max_length=100)

class InstantSearchForm(forms.Form):
    q = forms.CharField(max_length=100)

class SearchOneForm(forms.Form):
    q = forms.CharField(max_length=100)

