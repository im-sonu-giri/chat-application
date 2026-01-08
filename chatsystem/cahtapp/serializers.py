from .models import *
from rest_framework import serializers


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        models = User
        fields = ('id', 'username', 'password')
        
        def create(self, validate_data):
            user = User.objects.create_user(**validate_data)
            return user

class UserListSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'username')
        
class ConversationSerializer(serializers.ModelSerializer):
    participants = UserListSerializer(many=True, read_only= True)
    class Meta:
        model = Conversation
        fields = ('id', 'participants', 'created_at')
        
        def to_representation(self, instance):
            representation = super().to_representation(instance)
            return representation


class MessageSerializer(serializers.ModelSerializer):
    sender = UserListSerializer()
    participants = serializers.SerializerMethodField()
    class Meta:
        model = Message
        fields = ('id', 'conversation', 'sender', 'content', 'timestamp', 'participants')
        
        def get_participants(self, obj):
            return UserListSerializer(obj.conversation.participants.all(), many=True).data