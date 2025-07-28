# account/interfaces/serializers.py
from rest_framework import serializers


class RegisterSerializer(serializers.Serializer):
    username = serializers.CharField()
    email = serializers.EmailField(required=False, allow_blank=True)
    phone = serializers.CharField(required=False, allow_blank=True)
    password = serializers.CharField(write_only=True)


class LoginSerializer(serializers.Serializer):
    account = serializers.CharField()
    password = serializers.CharField(write_only=True)
