from django.contrib.auth.models import User
from django.db import models
from django.utils import timezone
from django.dispatch import receiver
from django.db.models.signals import post_save, post_delete

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

    def recount_votes(self):
        votes = QuestionVote.objects.filter(reference=self).aggregate(models.Sum('value'))
        self.votes = votes['value__sum']
        if self.votes == None:
            self.votes = 0
        self.save()

    def active_vote(self):
        if QuestionVote.objects.filter(reference=self, author=self.author).exists():
            existing_vote = QuestionVote.objects.get(reference=self, author=self.author)
            return existing_vote.value


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

    def recount_votes(self):
        votes = AnswerVote.objects.filter(reference=self).aggregate(models.Sum('value'))
        self.votes = votes['value__sum']
        if self.votes == None:
            self.votes = 0
        self.save()

    def active_vote(self):
        if AnswerVote.objects.filter(reference=self, author=self.author).exists():
            existing_vote = AnswerVote.objects.get(reference=self, author=self.author)
            return existing_vote.value


class AnswerVote(models.Model):
    reference = models.ForeignKey(Answer, on_delete=models.CASCADE, default=0)
    author = models.IntegerField(default=0)
    value = models.IntegerField(default=0)

@receiver(post_save, sender=AnswerVote)
def create_answer_vote(sender, instance, created, **kwargs):
    if created:
        instance.reference.recount_votes()

@receiver(post_save, sender=AnswerVote)
def update_answer_vote(sender, instance, **kwargs):
    instance.reference.recount_votes()

@receiver(post_delete, sender=AnswerVote)
def delete_answer_vote(sender, instance, **kwargs):
    instance.reference.recount_votes()


class QuestionVote(models.Model):
    reference = models.ForeignKey(Question, on_delete=models.CASCADE, default=0)
    author = models.IntegerField(default=0)
    value = models.IntegerField(default=0)

@receiver(post_save, sender=QuestionVote)
def create_quest_vote(sender, instance, created, **kwargs):
    if created:
        instance.reference.recount_votes()

@receiver(post_save, sender=QuestionVote)
def update_quest_vote(sender, instance, **kwargs):
    instance.reference.recount_votes()

@receiver(post_delete, sender=QuestionVote)
def delete_quest_vote(sender, instance, **kwargs):
    instance.reference.recount_votes()