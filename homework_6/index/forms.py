from django import forms

class SignupForm(forms.Form):
    login = forms.CharField(label='Login', max_length=200)
    email = forms.EmailField(label='Email', max_length=200)
    password = forms.CharField(widget=forms.PasswordInput, label='Password', max_length=200)
    password2 = forms.CharField(widget=forms.PasswordInput, label='Repeat password', max_length=200)
    avatar = forms.ImageField(label='Avatar')
