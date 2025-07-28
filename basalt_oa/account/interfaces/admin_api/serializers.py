# account/interfaces/serializers.py
from rest_framework import serializers
from account.infrastructure.orm_models import User


class RegisterSerializer(serializers.Serializer):
    username = serializers.CharField()
    email = serializers.EmailField(required=False, allow_blank=True)
    phone = serializers.CharField(required=False, allow_blank=True)
    password = serializers.CharField(write_only=True)


class LoginSerializer(serializers.Serializer):
    account = serializers.CharField()
    password = serializers.CharField(write_only=True)


class UserListSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['uuid', 'unified_uuid', 'username', 'email', 'phone', 'is_active', 'is_staff', 'is_superuser']
