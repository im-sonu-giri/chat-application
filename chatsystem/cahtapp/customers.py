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
            
    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        event_type = text_data_json.get('type')
        
        if event_type == 'chat_message':
            message_content = text_data_json.get('message')
            user_id = text_data_json.get('user')
            try:
                user = await self.get_user(user_id)
                conversation = await self.get_conversation(self.conversation_id)
                from .serializers import UserListSerializer
                user_data = UserListSerializer(user).data
                
                #msg to group
                
                message = await self.save_message(conversation, user, message_content)
                await self.channel_layer.group_send(
                    self.room_group_send,{
                        
                        'type': 'chat_message',
                        'message': message.content,
                        'user': user_data,
                        'timestamp': message.timestamp.isoformat(),
                        
                    }
                )
                
            except Exception as e:
                print(f"error saving message :{e}")
        
        elif event_type == 'typing':
            try:
                user_data = await self.get_user_data(self.scope['user'])
                receiver_id = text_data_json.get('receiver')
                
                if receiver_id is not None:
                    if isinstance(receiver_id, (str, int, float)):
                        receiver_id = int(receiver_id)
                        
                        if receiver_id != self.scope['user'].id:
                            print(f"{user_data['username']} is typing for receiver: {receiver_id}")
                            await self.channel_layer.group_send(
                                self.room_group_name,
                                {
                                    'type': 'typing',
                                    'user': user_data,
                                    'receiver': receiver_id,
                                }
                                }
                            )
                        else:
                            print(f"User is typing for themselves")
                    else:
                        print(f"Invalid receiver Id: {type(receiver_id)}")
                else:
                    print("No receiver is provided")
            except ValueError as e:
                print(f"Error parsing receiver Id: {e}")
            except Exception as e:
                print(f"Error getting user data: {e}")
                
             
    async def chat_message(self, event):
        message = event['message']
        user = event['user']
        timestamp =event['timestamp']
        await self.send(text_data=json.dumps)({
            'type': 'chat_message',
            'message': message,
            'user': user,
            'timestamp': timestamp,
        })
    async def typing(self, event):
        user = event['user']
        receiver = event.get('receiver')
        is_typing = event.get('is_typing', False)
        await self.send(text_data=json.dumps({
            'type': 'typing',
            'user': user,
            'receiver': receiver,
            'is_typing': is_typing,
        }))
        