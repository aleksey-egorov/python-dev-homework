from django import forms
from django.contrib.auth.models import User

from common.models import Profile

class UserForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ('email',)

class ProfileForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ('avatar',)

class SignupForm(forms.Form):
    login = forms.CharField(label='Login', max_length=200)
    email = forms.EmailField(label='Email', max_length=200)
    password = forms.CharField(widget=forms.PasswordInput, label='Password', max_length=200)
    password2 = forms.CharField(widget=forms.PasswordInput, label='Repeat password', max_length=200)
    avatar = forms.ImageField(label='Avatar')

    def clean_login(self):
        login = self.cleaned_data['login']
        if User.objects.filter(username=login).exists():
            raise forms.ValidationError('User with login "' + login+ '" already exists')
        return login

