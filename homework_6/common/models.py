import re

from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.mail import send_mail
from django.conf import settings


# Create your models here.

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    avatar = models.ImageField(null=True, blank=True, upload_to='avatars/')
    reg_date = models.ImageField(blank=True, default='NULL')

    @receiver(post_save, sender=User)
    def create_user_profile(sender, instance, created, **kwargs):
        if created:
            Profile.objects.create(user=instance)

    @receiver(post_save, sender=User)
    def save_user_profile(sender, instance, **kwargs):
        instance.profile.save()


class Mailer(models.Model):

    def send(self, email, alias, context):
        try:
            msg = settings.EMAIL_MESSAGES[alias]
            subject = msg[0]
            message = self.replace_context(msg[1], context) + settings.EMAIL_SIGN
            send_mail(subject, message,
                settings.EMAIL_FROM, [email],
                fail_silently=False,
            )
            return message
        except:
            pass

    def replace_context(self, msg, context):
        if isinstance(context, dict):
            for key in context.keys():
                tag = '<%' + str(key).upper() + '%>'
                msg = re.sub(tag, context[key], msg)

        return msg