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
        #validate jwt
        if token:
            try:
                decode_data = jwt.decode(token, settings.SECRET_KEY, algorithms=['HS256'])
                #get authenticated user
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
        #ADD logic:
        # Registers this connection into a group
        # Allows:
        # Broadcasting messages
        # Tracking online users
        # Group notifications
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        await self.accept()
        user_data = await self.get_user_data(self.user)
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'online status',
                'online_user': [user_data],
                'status': 'online',
            }
        )
    async def disconnect(self, close_code):
        if hasattr(self, 'room_group_name'):
            #notify about disconnection
            user_data = await self.user_data(self.scope['user'])
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                   'type': 'online_status',
                    'online_user': [user_data],
                    'status': 'offline',
                }
            )
            await self.channel_layer.group_discard(
                self.room_group_name,
                self.channel_layer
            )
            
    