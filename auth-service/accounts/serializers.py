from rest_framework import serializers
# from .models import User
from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password

User = get_user_model()
class RegisterSerializer(serializers.Serializer):
    username = serializers.CharField()
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True,
                                     validators=[validate_password])


    def validate_username(self,value):
        if User.objects.filter(username = value).exists():
            raise serializers.ValidationError(
                "this username already exists"
            )

        return value

    def create(self,validated_data):
        return User.objects.create_user(**validated_data)
            