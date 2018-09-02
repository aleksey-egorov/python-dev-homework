from django import forms

class LoginForm(forms.Form):
    login = forms.CharField(label='Login', max_length=100)
    password = forms.CharField(widget=forms.PasswordInput(), label='Password', max_length=100)