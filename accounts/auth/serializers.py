from django.contrib.auth.password_validation import (
    validate_password as django_validate_password,
)
from django.core.exceptions import ValidationError as DjangoValidationError
from django.db import transaction
from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

from accounts.models import Profile, User


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ("id", "email")


class RegisterSerializer(serializers.ModelSerializer):
    password_confirm = serializers.CharField(
        required=True,
        write_only=True,
    )

    class Meta:
        model = User
        fields = (
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
            },
        }

    def validate_email(self, value):
        user = User.objects.filter(email__iexact=value)

        if user.exists():
            raise serializers.ValidationError("Email Adresse bereits in nutzung.")

        return value.lower()

    def validate_password(self, value):
        try:
            django_validate_password(value)
        except DjangoValidationError as exc:
            raise serializers.ValidationError(list(exc.messages))

        return value

    def validate_tos_accepted(self, value):
        if value is not True:
            raise serializers.ValidationError("Bitte akzeptiere die AGB.")

        return value

    def validate(self, attrs):
        if attrs["password"] != attrs["password_confirm"]:
            raise serializers.ValidationError(
                {"password_confirm": "Passwörter stimmen nicht überein."}
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
