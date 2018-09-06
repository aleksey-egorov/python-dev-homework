from django.contrib.auth.models import User
from django.db import models
from django.utils import timezone

# Create your models here.

class Question(models.Model):
    heading = models.CharField(max_length=255)
    content = models.TextField()
    tags = models.CharField(max_length=255)
    pub_date = models.DateTimeField('date published')
    votes = models.IntegerField(default=0)
    answers = models.IntegerField(default=0)
    author = models.IntegerField(default=0)

    def published(self):
        delta = timezone.now() - self.pub_date
        if delta.days > 0:
            name = "day" if delta.days == 1 else "days"
            return str(delta.days) + " " + name
        elif delta.seconds > 3600:
            hours = delta.seconds // 3600
            name = "hour" if hours == 1 else "hours"
            return str(hours) + " " + name
        elif delta.seconds > 60:
            mins = delta.seconds // 60
            name = "minute" if mins == 1 else "minutes"
            return str(mins) + " " + name
        elif delta.seconds > 0:
            name = "sec" if delta.seconds == 1 else "seconds"
            return str(delta.seconds) + " " + name

    def author_name(self):
        user = User.objects.get(id=self.author)
        return user.username


class Trend(object):
    @staticmethod
    def get_trends():
        return Question.objects.order_by('-votes')[:5]


class Answer(models.Model):
    content = models.TextField()
    question_id = models.IntegerField(default=0)
    author = models.IntegerField(default=0)
    pub_date = models.DateTimeField('date published')
    votes = models.IntegerField(default=0)


class AnswerVote(models.Model):
    reference = models.ForeignKey(Answer, on_delete=models.CASCADE, default=0)
    author = models.IntegerField(default=0)
    value = models.IntegerField(default=0)


class QuestionVote(models.Model):
    reference = models.ForeignKey(Question, on_delete=models.CASCADE, default=0)
    author = models.IntegerField(default=0)
    value = models.IntegerField(default=0)