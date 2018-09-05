from django import forms

class AskForm(forms.Form):
    heading = forms.CharField(label='Heading', max_length=200)
    content = forms.CharField(label='Content', widget=forms.Textarea)
    tags = forms.CharField(label='Tags', max_length=200)

class AnswerForm(forms.Form):
    answer = forms.CharField(label='', widget=forms.Textarea)
