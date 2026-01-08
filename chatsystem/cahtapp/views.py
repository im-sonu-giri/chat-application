from django.shortcuts import render
from rest_framework import generics, permissions, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404
from .models import *
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