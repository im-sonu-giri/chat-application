from django.shortcuts import render
from rest_framework import generics, permissions, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404
from .models import Conversation, Message


from .serializers import *
from rest_framework.exceptions import PermissionDenied


class CreateUserView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    
class UserListView(generics.ListAPIView):
    queryset = User.objects.all()
    serializer_class = UserListSerializer
    permission_classes = [IsAuthenticated]
    

class ConversationListCreateView(generics.ListCreateAPIView):
    serializer_class = ConversationSerializer
    permission_classes = [IsAuthenticated]
    def get_queryset(self):
        return (Conversation.objects.filter(participants=self.request.user).prefetch_related('participants'))
    
    def create(self, request, *args, **kwargs):
        participants_data = request.data.pop('participants', [])
        
        if len(participants_data) != 2:
            return Response(
                {'error': 'Conversation needs exactly two Participanta'},
                status=status.HTTP_400_BAD_REQUEST
            )
        if str(request.user.id) not in map(str, participants_data):
            return Response(
                {
                    'error': 'you are not participant of this conversation'
                },
                status=status.HTTP_403_FORBIDDEN
            )
            
        users = User.objects.filter(id_in=participants_data)
        if users.count()!=2:
            return Response(
                {
                    'error':"conversation needs two participants"
                }, 
                status=status.HTTP_400_BAD_REQUEST
            )
        existing_conversation = Conversation.objects.filter(
            participants__id= participants_data[0]
        ).filter(participants__id=participants_data[1]).distinct()
        
        if existing_conversation.exists():
            return Response(
                {
                "error": "conversation already exist"
                }, 
                status=status.HTTP_400_BAD_REQUEST
            )
        conversation = Conversation.objects.create()
        conversation.participants.set(users)
        
        serializer = self.get_serializer(conversation)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
        
#Logic: 

# GET list of conversations where current user is a participant

# WHEN create request is received:

#     Extract "participants" from request data
#     If participants count is NOT equal to 2:
#         RETURN error "Conversation needs exactly two participants"

#     If current user ID is NOT in participants list:
#         RETURN error "You are not a participant of this conversation"

#     Fetch users from database whose IDs are in participants list

#     If number of fetched users is NOT equal to 2:
#         RETURN error "Conversation needs two valid users"

#     Check if a conversation already exists such that:
#         - participant 1 exists in the conversation
#         - participant 2 exists in the conversation

#     If such conversation exists:
#         RETURN error "Conversation already exists"

#     Create a new empty conversation

#     Add both users as participants of the conversation

#     RETURN success response


class MessageListCreateView(generics.ListCreateAPIView):
    permission_classes = [IsAuthenticated]
    def get_queryset(self):
        conversation_id = self.kwargs['conversation_id']
        conversation = self.get_conversation(conversation_id)
        
        return conversation.messages.order_by('timestamp')
    
    def get_conversation(self):
        if self.request.method == 'POST':
            return CreateMessageSerializer
        return MessageSerializer
    def perform_create(self, serializer):
        print('Incomming conversation', self.request.data)
        conversation_id = self.kwargs['conversation_id']
        conversation =self.get_conversation(conversation_id)
        serializer.save(sender=self.request.user, conversation=conversation)
        
    def get_conversation(self, conversation_id):
        conversation = get_object_or_404(conversation, id=conversation_id)
        if self.request.user not in conversation.participants.all():
            raise PermissionDenied('you are not a participant of this conversation')
        return conversation
    
class MessageRetrieveDestroyView(generics.RetrieveAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = MessageSerializer
    
    def get_queryset(self):
        conversation_id= self.kwargs['conversation_id']
        return Message.objects.filter(conversation_id= conversation_id)
    
    def perform_destroy(self, instance):
        if instance.sender!= self.request.user:
            raise PermissionDenied('you are not the sender of this message')
        instance.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
   