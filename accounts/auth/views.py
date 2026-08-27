from django.conf import settings
from rest_framework import generics, status
from rest_framework.permissions import AllowAny
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework_simplejwt.exceptions import InvalidToken, TokenError
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import (
    TokenBlacklistView,
    TokenObtainPairView,
    TokenRefreshView,
)

from .serializers import LoginSerializer, RegisterSerializer, UserSerializer


class RegisterView(generics.CreateAPIView):
    serializer_class = RegisterSerializer
    permission_classes = [AllowAny]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)

        refresh_token = RefreshToken.for_user(user)

        response = Response(
            {
                "user": UserSerializer(user).data,
                "access": str(refresh_token.access_token),
            },
            status=status.HTTP_201_CREATED,
            headers=headers,
        )

        response.set_cookie(
            settings.AUTH_COOKIE["NAME"],
            value=str(refresh_token),
            max_age=settings.SIMPLE_JWT["REFRESH_TOKEN_LIFETIME"],
            secure=settings.AUTH_COOKIE["SECURE"],
            httponly=True,
            samesite=settings.AUTH_COOKIE["SAMESITE"],
            path=settings.AUTH_COOKIE["PATH"],
        )
        return response

    def perform_create(self, serializer):
        return serializer.save()


class LoginView(TokenObtainPairView):
    serializer_class = LoginSerializer

    def post(self, request: Request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)

        try:
            serializer.is_valid(raise_exception=True)
        except TokenError as e:
            raise InvalidToken(e.args[0]) from e

        refresh_token = serializer.validated_data.pop("refresh")

        response = Response(serializer.validated_data, status=status.HTTP_200_OK)
        response.set_cookie(
            settings.AUTH_COOKIE["NAME"],
            value=str(refresh_token),
            max_age=settings.SIMPLE_JWT["REFRESH_TOKEN_LIFETIME"],
            secure=settings.AUTH_COOKIE["SECURE"],
            httponly=True,
            samesite=settings.AUTH_COOKIE["SAMESITE"],
            path=settings.AUTH_COOKIE["PATH"],
        )

        return response


class LogoutView(TokenBlacklistView):
    def post(self, request: Request, *args, **kwargs):
        cookie = {"refresh": request.COOKIES.get(settings.AUTH_COOKIE["NAME"])}
        response = Response(status=status.HTTP_204_NO_CONTENT)

        if not cookie["refresh"]:
            return response

        serializer = self.get_serializer(data=cookie)

        try:
            serializer.is_valid(raise_exception=True)
        except TokenError:
            pass

        response.delete_cookie(
            settings.AUTH_COOKIE["NAME"],
            path=settings.AUTH_COOKIE["PATH"],
        )

        return response


class CurrentUserView(generics.RetrieveAPIView):
    serializer_class = UserSerializer

    def get_object(self):
        return self.request.user


class CookieTokenRefreshView(TokenRefreshView):
    def post(self, request: Request, *args, **kwargs):
        cookie = {"refresh": request.COOKIES.get(settings.AUTH_COOKIE["NAME"])}

        if not cookie["refresh"]:
            raise InvalidToken("Kein Refresh-Token vorhanden.")

        serializer = self.get_serializer(data=cookie)

        try:
            serializer.is_valid(raise_exception=True)
        except TokenError as e:
            raise InvalidToken(e.args[0]) from e

        refresh_token = serializer.validated_data.pop("refresh")

        response = Response(serializer.validated_data, status=status.HTTP_200_OK)
        response.set_cookie(
            settings.AUTH_COOKIE["NAME"],
            value=str(refresh_token),
            max_age=settings.SIMPLE_JWT["REFRESH_TOKEN_LIFETIME"],
            secure=settings.AUTH_COOKIE["SECURE"],
            httponly=True,
            samesite=settings.AUTH_COOKIE["SAMESITE"],
            path=settings.AUTH_COOKIE["PATH"],
        )

        return response
