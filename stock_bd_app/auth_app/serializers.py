from rest_framework import serializers
# from django.contrib.auth import get_user_model
from rest_framework.fields import CharField
from auth_app.models import CustomUser


# class UserSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = get_user_model()
#         fields = ['username', 'email']

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ('username',)


class RegistrationSerializer(serializers.ModelSerializer):
    password2 = serializers.CharField(write_only=True)

    class Meta:
        # model = get_user_model()
        model = CustomUser
        fields = ['username', 'email', 'password', 'password2']
        extra_kwargs = {
            'password': {'write_only': True}
        }

    def create(self, validated_data):
        password = validated_data.pop('password')
        password2 = validated_data.pop('password2')
        if password != password2:
            raise serializers.ValidationError("Passwords do not match.")
        user = self.Meta.model(**validated_data)
        user.set_password(password)
        user.save()
        return user


# class LoginSerializer(serializers.Serializer):
#     username = serializers.CharField()
#     password = serializers.CharField()

class LoginSerializer(serializers.ModelSerializer):
    username = CharField(max_length=150, help_text='Enter username')

    class Meta:
        model = CustomUser
        fields = ('username', 'password')

    