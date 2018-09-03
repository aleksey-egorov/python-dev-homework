from django import forms

class AskForm(forms.Form):
    heading = forms.CharField(label='Heading', max_length=100)
    content = forms.CharField(label='Content')