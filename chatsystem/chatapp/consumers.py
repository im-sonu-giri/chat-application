from asgiref.sync import sync_to_async
import json
import jwt
from channels.generic.websocket import AsyncWebsocketConsumer
from django.contrib.auth import get_user_model
from django.conf import settings
from urllib.parse import parse_qs


User = get_user_model()


class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        # Parse JWT token from query params
        query_string = self.scope['query_string'].decode('utf8')
        params = parse_qs(query_string)
        token = params.get('token', [None])[0]

        if not token:
            await self.close(code=4002)  # Token not provided
            return

        try:
            decode_data = jwt.decode(token, settings.SECRET_KEY, algorithms=['HS256'])
            self.user = await self.get_user(decode_data['user_id'])
            self.scope['user'] = self.user
        except jwt.ExpiredSignatureError:
            await self.close(code=4000)  # Token expired
            return
        except jwt.InvalidTokenError:
            await self.close(code=4001)  # Invalid token
            return

      
        self.room_group_name = 'chat_global'

        # Add to group
        await self.channel_layer.group_add(self.room_group_name, self.channel_name)
        await self.accept()

        # Notify group that user is online
        user_data = await self.get_user_data(self.user)
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'online_status',
                'online_user': [user_data],
                'status': 'online',
            }
        )

    async def disconnect(self, close_code):
        if hasattr(self, 'room_group_name'):
            # Notify group user went offline
            user_data = await self.get_user_data(self.scope['user'])
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'online_status',
                    'online_user': [user_data],
                    'status': 'offline',
                }
            )
            # Remove from group
            await self.channel_layer.group_discard(self.room_group_name, self.channel_name)

    async def receive(self, text_data):
        data = json.loads(text_data)
        event_type = data.get('type')

        if event_type == 'chat_message':
            message_content = data.get('message')
            user_id = data.get('user')
            conversation_id = data.get('conversation_id')  # Pass conversation_id from frontend

            try:
                user = await self.get_user(user_id)
                conversation = await self.get_conversation(conversation_id)
                if conversation is None:
                    return

                from .serializers import UserListSerializer
                user_data = UserListSerializer(user).data

                message = await self.save_message(conversation, user, message_content)

                # Send to group
                await self.channel_layer.group_send(
                    self.room_group_name,
                    {
                        'type': 'chat_message',
                        'message': message.content,
                        'user': user_data,
                        'timestamp': message.timestamp.isoformat(),
                    }
                )
            except Exception as e:
                print(f"Error saving message: {e}")

        elif event_type == 'typing':
            try:
                user_data = await self.get_user_data(self.scope['user'])
                receiver_id = data.get('receiver')

                if receiver_id is not None and isinstance(receiver_id, (str, int, float)):
                    receiver_id = int(receiver_id)
                    if receiver_id != self.scope['user'].id:
                        await self.channel_layer.group_send(
                            self.room_group_name,
                            {
                                'type': 'typing',
                                'user': user_data,
                                'receiver': receiver_id,
                                'is_typing': True,
                            }
                        )
            except Exception as e:
                print(f"Error handling typing event: {e}")

    # ---------------- WebSocket event handlers ----------------
    async def chat_message(self, event):
        await self.send(text_data=json.dumps({
            'type': 'chat_message',
            'message': event['message'],
            'user': event['user'],
            'timestamp': event['timestamp'],
        }))

    async def typing(self, event):
        await self.send(text_data=json.dumps({
            'type': 'typing',
            'user': event['user'],
            'receiver': event.get('receiver'),
            'is_typing': event.get('is_typing', False),
        }))

    async def online_status(self, event):
        await self.send(text_data=json.dumps(event))

    @sync_to_async
    def get_user(self, user_id):
        return User.objects.get(id=user_id)

    @sync_to_async
    def get_user_data(self, user):
        from .serializers import UserListSerializer
        return UserListSerializer(user).data

    @sync_to_async
    def get_conversation(self, conversation_id):
        from .models import Conversation
        try:
            return Conversation.objects.get(id=conversation_id)
        except Conversation.DoesNotExist:
            print(f"Conversation with id {conversation_id} does not exist")
            return None

    @sync_to_async
    def save_message(self, conversation, user, content):
        from .models import Message
        return Message.objects.create(
            conversation=conversation,
            sender=user,
            content=content
        )
