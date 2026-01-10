from asgiref.sync import sync_to_async
import json
import jwt
from channels.generic.websocket import AsyncWebsocketConsumer
from django.contrib.auth  import get_user_model
from django.conf import settings
from .models import *
from urllib.parse import parse_qs


User = get_user_model()

class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        query_string = self.scope['query_string'].decode('utf8')
        params = parse_qs(query_string)
        token = params.get('token', [None])[0]