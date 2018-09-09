from django.shortcuts import render
from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator
from django.views.generic import View
from django.contrib.auth.models import User
from django.http import HttpResponseRedirect
from django.db import transaction

from question.models import Question, Trend
from index.forms import SignupForm, UserForm, ProfileForm

# Create your views here.

class IndexView(View):

    def get(self, request):
        quest_list = Question.objects.order_by('-pub_date')[:10]
        paginator = Paginator(quest_list, 10)
        page = request.GET.get('page')
        questions = paginator.get_page(page)

        return render(request, "index/index.html", {"questions": questions, "trends": Trend.get_trends() })


class SignupView(View):

    def get(self, request):
        form = SignupForm()

        return render(request, "index/signup.html", {
            "form": form,
            "trends": Trend.get_trends()
        })

    def post(self, request):
        form = SignupForm(request.POST, request.FILES)
        if form.is_valid():
            # Creating user and profile
            with transaction.atomic():
                new_user = User(username=form.cleaned_data['login'],
                                password=form.cleaned_data['password'],
                                email=form.cleaned_data['email'])
                new_user.save()
            new_user.profile.avatar = form.cleaned_data['avatar']
            new_user.profile.save()

            return HttpResponseRedirect('/signup/done/')
        else:
            message = 'Error while adding new user ' + str(form.cleaned_data)
        return render(request, "index/signup.html", {
            "form": form,
            "message": message,
            "trends": Trend.get_trends()
        })


class SignupDoneView(View):

    def get(self, request):
        return render(request, "index/signup_done.html", {
            "trends": Trend.get_trends()
        })


class UserSettingsView(View):

    def get(self, request):
        return render(request, "index/settings.html", {
            "trends": Trend.get_trends()
        })

    def post(self, request):
        user_form = UserForm(request.POST, instance=request.user)
        profile_form = ProfileForm(request.POST, request.FILES,instance=request.user.profile)
        if user_form.is_valid() and profile_form.is_valid():
            with transaction.atomic():
                user_form.save()
                profile_form.save()
            message = 'User settings successfully updated'
        else:
            message = 'Error while updating user'
        return render(request, "index/settings.html", {
            "user_form": user_form,
            "profile_form": profile_form,
            "message": message,
            "trends": Trend.get_trends()
        })