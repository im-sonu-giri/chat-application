from django.db import models
from django.contrib.auth.models import User
from django.db.models import Prefetch #helps to solve the N+1 problem

class ConversationManger(models.Manager):
    def get_queryset(self):
        return super().get_queryset().prefetch_related(
            Prefetch('participants', queryset=User.objects.only('id', 'username'))
        )



class Conversation(models.Model):
    participants =  models.ManyToManyField(User, related_name='conversations')
    objects = ConversationManger()
    
    def __str__(self):
        participant_names = " ,".join([user.username for user in self.participants.all()])
        return f"conversation with {participant_names}"