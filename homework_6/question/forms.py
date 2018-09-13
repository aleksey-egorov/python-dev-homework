from django import forms


class AskForm(forms.Form):
    heading = forms.CharField(label='Heading', max_length=200)
    content = forms.CharField(label='Content', widget=forms.Textarea)
    tags = forms.CharField(label='Tags', max_length=200)

    def clean_tags(self):
        dtags = self.cleaned_data['tags'].split(",")
        if len(dtags) > 3:
            raise forms.ValidationError('You can use up to 3 tags')
        return self.cleaned_data['tags']


class AnswerForm(forms.Form):
    answer = forms.CharField(label='', widget=forms.Textarea)
