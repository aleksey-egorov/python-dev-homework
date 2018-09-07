import datetime
from django.shortcuts import render
from django.http import HttpResponseRedirect
from django.views.generic import View
from django.db import transaction

from question.models import Question, Trend, Answer, AnswerVote, QuestionVote
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
        answers = Answer.objects.filter(question=quest)

        return render(request, "question/question.html", {
            "trends": Trend.get_trends(),
            "form": form.as_ul(),
            "question": quest,
            "answers": answers
        })

    def post(self, request, id):
        form = AnswerForm(request.POST)
        if form.is_valid():
            quest = Question.objects.get(id=id)
            new_answer = Answer(content=form.cleaned_data['answer'],
                                  question=quest,
                                  pub_date=datetime.datetime.now(),
                                  author=request.user.id)
            new_answer.save()
            return HttpResponseRedirect('/question/' + str(new_answer.question.id) + '/')
        else:
            message = 'Error while adding'
            return render(request, "question/question.html", {
                "form": form.as_ul(),
                "id": id,
                "message": message,
                "trends": Trend.get_trends()
            })


class VoteView(View):

    def get(self, request):
        type =  request.GET.get('type')
        obj_id = int(request.GET.get('id'))
        value = request.GET.get('value')

        result = 'error'
        votes = 0
        if type in ('answer', 'question') and obj_id > 0 and value in ('up', 'down'):
            if value == 'up':
                val = 1
            else:
                val = -1
            if type == 'answer':
                vote = AnswerVote
                ref_obj = Answer.objects.get(id=obj_id)
            else:
                vote = QuestionVote
                ref_obj = Question.objects.get(id=obj_id)

            if vote.objects.filter(reference=ref_obj, author=request.user.id).exists():
                existing_vote = vote.objects.get(reference=ref_obj, author=request.user.id)
                if existing_vote.value == val:
                    existing_vote.delete()
                    result = 'delete'
                else:
                    existing_vote.value = val
                    existing_vote.save()
                    result = 'update'
                votes = existing_vote.reference.votes
            else:
                new_vote = vote(reference=ref_obj,
                                author=request.user.id,
                                value=val)
                new_vote.save()
                result = 'add'
                votes = new_vote.reference.votes

        return render(request, "question/vote.html", {
            "result": result,
            "votes": votes
        })


class BestAnswerView(View):

    def get(self, request):
        answer_id = int(request.GET.get('id'))
        answer = Answer.objects.get(id=answer_id)

        result = 'error'
        if answer.author == request.user.id:
            with transaction.atomic():
                if answer.best == True:
                    answer.best = False
                    answer.save()
                    result = 'delete'
                else:
                    Answer.objects.filter(question=answer.question).update(best=False)
                    answer.best = True
                    answer.save()
                    result = 'update'

        return render(request, "question/best.html", {
            "result": result
        })