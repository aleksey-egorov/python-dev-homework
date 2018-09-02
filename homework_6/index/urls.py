from django.conf.urls import url
from .views import IndexView

app_name = 'index'

urlpatterns = [
    url('', IndexView.as_view()),
]