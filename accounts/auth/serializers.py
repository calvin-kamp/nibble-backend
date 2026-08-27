from django.contrib.auth.password_validation import (
    validate_password as django_validate_password,
)
from django.core.exceptions import ValidationError as DjangoValidationError
from django.db import transaction
from rest_framework import serializers
from rest_framework.validators import UniqueValidator
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

from accounts.models import Profile, User


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ("id", "email")


class RegisterSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(
        required=True,
        validators=[
            UniqueValidator(
                queryset=User.objects.all(),
                lookup="iexact",
                message="Diese E-Mail-Adresse wird bereits verwendet.",
            )
        ],
    )
    password_confirm = serializers.CharField(
        required=True,
        write_only=True,
    )

    class Meta:
        model = User
        fields = (
            "id",
            "email",
            "password",
            "password_confirm",
            "tos_accepted",
        )
        extra_kwargs = {
            "password": {
                "write_only": True,
            },
            "tos_accepted": {
                "required": True,
                "write_only": True,
                "error_messages": {
                    "required": "Bitte stimme den AGB zu.",
                },
            },
        }

    def validate_email(self, value):
        return value.lower()

    def validate_password(self, value):
        try:
            django_validate_password(value)
        except DjangoValidationError as exc:
            raise serializers.ValidationError(list(exc.messages))

        return value

    def validate_tos_accepted(self, value):
        if value is not True:
            raise serializers.ValidationError("Bitte stimme den AGB zu.")

        return value

    def validate(self, attrs):
        if attrs["password"] != attrs["password_confirm"]:
            raise serializers.ValidationError(
                {"password_confirm": "Die Passwörter stimmen nicht überein."}
            )

        return attrs

    def create(self, validated_data):
        email = validated_data.pop("email")
        password = validated_data.pop("password")
        validated_data.pop("password_confirm")

        with transaction.atomic():
            user = User.objects.create_user(email, password, **validated_data)
            Profile.objects.create(user=user)

        return user


class LoginSerializer(TokenObtainPairSerializer):
    def validate(self, attrs):
        data = super().validate(attrs)
        data["user"] = UserSerializer(self.user).data

        return data
