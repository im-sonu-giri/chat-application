from asgiref.sync import sync_to_async
import json
import jwt
from channels.generic.websocket import AsyncWebsocketConsumer
from django.contrib.auth  import get_user_model
from django.conf import settings
from .models import *