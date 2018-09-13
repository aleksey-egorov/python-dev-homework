import datetime
from django.shortcuts import render
from django.http import HttpResponseRedirect
from django.views.generic import View
from django.db import transaction
from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator
from django.db.models import Q
from django.contrib.auth.mixins import LoginRequiredMixin
from django.conf import settings

from common.models import Mailer
from question.models import Question, Trend, Answer, AnswerVote, QuestionVote
from .forms import AskForm, AnswerForm

# Create your views here.

class AskView(LoginRequiredMixin, View):

    def get(self, request):
        form = AskForm()
        return render(request, "question/ask.html", {
            "trends": Trend.get_trends(),
            "form": form
        })

    def post(self, request):
        form = AskForm(request.POST)
        if form.is_valid():
            new_question = Question(heading=form.cleaned_data['heading'],
                                    content=form.cleaned_data['content'],
                                    tags=form.cleaned_data['tags'],
                                    pub_date=datetime.datetime.now(),
                                    author=request.user)
            new_question.save()
            return HttpResponseRedirect('/question/' + str(new_question.id) + '/')
        else:
            message = 'Error while adding'
            return render(request, "question/ask.html", {
                "form": form,
                "message": message,
                "trends": Trend.get_trends()
            })


class QuestionView(View):

    def get(self, request, id):
        form = AnswerForm()
        quest = Question.objects.get(id=id)
        answers_set = Answer.objects.filter(question=quest).order_by('-votes','-pub_date')
        quest.active_user_vote = quest.active_vote(request.user.id)
        answers = []
        for answer in answers_set:
            answer.active_user_vote = answer.active_vote(request.user.id)
            answers.append(answer)

        paginator = Paginator(answers, 30)
        page = request.GET.get('page')
        answers = paginator.get_page(page)

        return render(request, "question/question.html", {
            "trends": Trend.get_trends(),
            "form": form,
            "question": quest,
            "answers": answers
        })

    def post(self, request, id):
        if request.user.is_authenticated:
            form = AnswerForm(request.POST)
            if form.is_valid():
                quest = Question.objects.get(id=id)
                new_answer = Answer(content=form.cleaned_data['answer'],
                                      question=quest,
                                      pub_date=datetime.datetime.now(),
                                      author=request.user)
                new_answer.save()

                url = 'http://' + settings.SITE_URL + '/question/' + str(new_answer.question.id) + '/'
                link = '<a href="'+ url +'">' + url + '</a>'
                Mailer().send(quest.author.email, 'new_answer', context={"link": link})

                return HttpResponseRedirect(url)
            else:
                message = 'Error while adding'

                return render(request, "question/question.html", {
                    "form": form,
                    "id": id,
                    "message": message,
                    "trends": Trend.get_trends()
                })


class VoteView(LoginRequiredMixin, View):

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

            if vote.objects.filter(reference=ref_obj, author=request.user).exists():
                existing_vote = vote.objects.get(reference=ref_obj, author=request.user)
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
                                author=request.user,
                                value=val)
                new_vote.save()
                result = 'add'
                votes = new_vote.reference.votes

        return render(request, "question/vote.html", {
            "result": result,
            "votes": votes
        })


class BestAnswerView(LoginRequiredMixin, View):

    def get(self, request):
        answer_id = int(request.GET.get('id'))
        answer = Answer.objects.get(id=answer_id)

        result = 'error'
        if answer.question.author == request.user:
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


class SearchView(View):

    def get(self, request):
        query = request.GET.get('q')
        quest_list = Question.objects.filter(Q(heading__icontains=query) | Q(content__icontains=query)).order_by('votes','-pub_date')[:20]
        paginator = Paginator(quest_list, 20)
        page = request.GET.get('page')
        questions = paginator.get_page(page)

        return render(request, "question/search.html", {
            "questions": questions,
            "query": query,
            "trends": Trend.get_trends()
        })


class TagView(View):

    def get(self, request, tag):
        tag = str(tag).strip()
        quest_list = Question.objects.filter(tags__icontains=tag).order_by('votes','-pub_date')[:20]
        paginator = Paginator(quest_list, 20)
        page = request.GET.get('page')

        try:
            questions = paginator.get_page(page)
        except PageNotAnInteger:
            questions = paginator.get_page(1)
        except EmptyPage:
            questions = paginator.get_page(page)

        return render(request, "question/search.html", {
            "questions": questions,
            "query": "tag:{}".format(tag),
            "trends": Trend.get_trends()
        })


class QuestionListView(View):

    def get(self, request):
        page = request.GET.get('page')
        sort = request.GET.get('sort')
        if sort == 'date':
            sort_1 = '-pub_date'
            sort_2 = '-votes'
        else:
            sort_1 = '-votes'
            sort_2 = '-pub_date'
        quest_list = Question.objects.order_by(sort_1, sort_2)
        paginator = Paginator(quest_list, 20)

        try:
            questions = paginator.get_page(page)
        except PageNotAnInteger:
            questions = paginator.get_page(1)
        except EmptyPage:
            questions = paginator.get_page(page)

        return render(request, "question/list.html", {
            "questions": questions,
            "trends": Trend.get_trends()
        })