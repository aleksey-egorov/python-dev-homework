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
    author = models.ForeignKey(User, on_delete=models.CASCADE, default=0)

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
        return self.author.username

    def author_avatar(self):
        return self.author.profile.avatar

    def tags_list(self):
        list = self.tags.split(",")
        list = [x.strip() for x in list]
        return list

    def recount_votes(self):
        votes = QuestionVote.objects.filter(reference=self).aggregate(models.Sum('value'))
        self.votes = votes['value__sum']
        if self.votes == None:
            self.votes = 0
        self.save()

    def recount_answers(self):
        self.answers = Answer.objects.filter(question=self).count()
        if self.answers == None:
            self.answers = 0
        self.save()

    def active_vote(self, user_id):
        if QuestionVote.objects.filter(reference=self, author=user_id).exists():
            existing_vote = QuestionVote.objects.get(reference=self, author=user_id)
            return existing_vote.value


class Trend(object):
    @staticmethod
    def get_trends():
        return Question.objects.order_by('-votes')[:5]


class Answer(models.Model):
    content = models.TextField()
    question = models.ForeignKey(Question, on_delete=models.CASCADE, default=0)
    author = models.ForeignKey(User, on_delete=models.CASCADE, default=0)
    pub_date = models.DateTimeField('date published')
    votes = models.IntegerField(default=0)
    best = models.BooleanField(default=False)

    def recount_votes(self):
        votes = AnswerVote.objects.filter(reference=self).aggregate(models.Sum('value'))
        self.votes = votes['value__sum']
        if self.votes == None:
            self.votes = 0
        self.save()

    def author_name(self):
        return self.author.username

    def author_avatar(self):
        return self.author.profile.avatar

    def active_vote(self, user_id):
        if AnswerVote.objects.filter(reference=self, author=user_id).exists():
            existing_vote = AnswerVote.objects.get(reference=self, author=user_id)
            return existing_vote.value

@receiver(post_save, sender=Answer)
def create_answer(sender, instance, created, **kwargs):
    if created:
        instance.question.recount_answers()

@receiver(post_save, sender=Answer)
def update_answer(sender, instance, **kwargs):
    instance.question.recount_answers()

@receiver(post_delete, sender=Answer)
def delete_answer(sender, instance, **kwargs):
    instance.question.recount_answers()


class AnswerVote(models.Model):
    reference = models.ForeignKey(Answer, on_delete=models.CASCADE, default=0)
    author = models.ForeignKey(User, on_delete=models.CASCADE, default=0)
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
    author = models.ForeignKey(User, on_delete=models.CASCADE, default=0)
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