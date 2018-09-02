from django.shortcuts import render
from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator
from django.views.generic import View
from question.models import Question, Trend


# Create your views here.

class IndexView(View):

    def get(self, request):
        quest_list = Question.objects.order_by('-pub_date')[:10]
        paginator = Paginator(quest_list, 10)
        page = request.GET.get('page')
        questions = paginator.get_page(page)

        return render(request, "index/index.html", {"questions": questions, "trends": Trend.get_trends() })



