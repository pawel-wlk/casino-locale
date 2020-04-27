from django.db import models
from django.contrib.auth.models import User
from django.dispatch import receiver
from django.db.models.signals import post_save


class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    coins = models.PositiveIntegerField(default=100)


@receiver(post_save, sender=User)
def extend_user(sender, instance, **kwargs):
    UserProfile(user=instance).save()
