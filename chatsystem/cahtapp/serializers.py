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