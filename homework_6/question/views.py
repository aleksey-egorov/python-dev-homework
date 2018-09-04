import datetime
from django.shortcuts import render
from django.http import HttpResponseRedirect
from django.views.generic import View

from question.models import Question, Trend
from .forms import AskForm, AnswerForm

# Create your views here.


class AskView(View):

    def get(self, request):
        form = AskForm()

        return render(request, "question/ask.html", {"trends": Trend.get_trends(), "form": form.as_ul() })

    def post(self, request):
        form = AskForm(request.POST)
        if form.is_valid():
            new_question = Question(heading=form.cleaned_data['heading'],
                                    content=form.cleaned_data['content'],
                                    tags=form.cleaned_data['tags'],
                                    pub_date=datetime.datetime.now(),
                                    author=request.user.id)
            new_question.save()
            return HttpResponseRedirect('/question/' + str(new_question.id) + '/')
        else:
            message = 'Error while adding'
            return render(request, "question/ask.html", {
                "form": form.as_ul(),
                "message": message,
                "trends": Trend.get_trends()
            })


class QuestionView(View):

    def get(self, request, id):
        form = AnswerForm()
        quest = Question.objects.get(id=id)

        return render(request, "question/question.html", {"trends": Trend.get_trends(), "form": form.as_ul(), "question": quest })