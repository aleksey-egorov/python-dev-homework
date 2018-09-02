from django.contrib.auth import authenticate, logout
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.views.generic import View

from auth.forms import LoginForm
from index.models import Trend


# Create your views here.

class LoginView(View):

    def get(self, request):
        message = ''
        form = LoginForm()

        return render(request, "auth/login.html", {
            "form": form.as_ul(),
            "message": message,
            "trends": Trend.get_trends()
        })


    def post(self, request):
        message = ''
        form = LoginForm(request.POST)

        if form.is_valid():
            user = authenticate(username=form.cleaned_data['login'], password=form.cleaned_data['password'])
            if user is not None:
                message = 'Success'
                #return HttpResponseRedirect('/')
            else:
                message = 'Authentication error: wrong username or password'
        else:
            message = 'Authentication error'

        return render(request, "auth/login.html", {
            "form": form.as_ul(),
            "message": message,
            "trends": Trend.get_trends()
        })


class LogoutView(View):

    def get(self, request):
        referer = request.META['HTTP_REFERER']
        logout(request)
        return HttpResponseRedirect(referer)