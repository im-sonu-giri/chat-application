from django.db import models
from django.contrib.auth.models import User
from django.db.models import Prefetch #helps to solve the N+1 problem

class ConversationManger(models.Manager):
    def get_queryset(self):
        return super().get_queryset().prefetch_related(
            Prefetch('participants', queryset=User.objects.only('id', 'username'))
        )



