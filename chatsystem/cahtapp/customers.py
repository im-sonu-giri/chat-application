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
        
        if token:
            try:
                decode_data = jwt.decode(token, settings.SECRET_KEY, algorithms=['HS256'])
                self.user = await self.get_user(decode_data['user_id'])
                self.scope['user']= self.user
            except jwt.ExpiredSignatureError:
                self.close(code=4000)
                #close the connection if token expired
                return
            except jwt.InvalidTokenError:
                self.close(code=4001)#close if token invalid
                return
        else:
            await self.close(code=4002)#close if token not provided
            return
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )