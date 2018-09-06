"""hasker URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, re_path, include
from django.contrib.auth import views as auth_views

from question.models import Trend
from question.views import AskView, QuestionView, VoteView

urlpatterns = [

    path('login/', auth_views.LoginView.as_view(
        extra_context={"trends": Trend.get_trends()}
    )),
    path('logout/', auth_views.LogoutView.as_view()),
    path('ask/', AskView.as_view()),
    path('question/<int:id>/', QuestionView.as_view(), name="question"),
    path('question/vote/', VoteView.as_view(), name="question_vote"),
    path('admin/', admin.site.urls),
    path('', include('index.urls')),
]
