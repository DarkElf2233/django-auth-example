from django.db import transaction
from django.http import Http404
from django.contrib.auth.models import User, Permission
from django.contrib.auth.hashers import make_password
from django.contrib.contenttypes.models import ContentType

from rest_framework import status
from rest_framework.generics import CreateAPIView
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny, IsAuthenticated, IsAdminUser
from rest_framework.response import Response
from rest_framework.exceptions import ValidationError

import requests

import environ
import secrets
import jwt

from app.serializers import UserSerializer, UserUpdateSerializer
from app.authentication import JWTAuthentication
from app.utils import (
    create_auth_token,
    create_username,
    send_password_notification_email,
    send_test_email,
    rate_limit,
    send_welcome_email,
    generate_email_change_token,
    send_confirmation_email,
)

env = environ.Env()


### AUTH ###


class ChangeEmailView(APIView):
    authentication_classes = [JWTAuthentication]

    def post(self, request):
        new_email = request.data.get("new_email")
        user_id = request.data.get("user_id")
        user = User.objects.get(id=user_id)
        token = generate_email_change_token(user, new_email)
        send_confirmation_email(user, token)

        return Response(
            {"detail": "Confirmation email sent."}, status=status.HTTP_200_OK
        )


class ConfirmEmailView(APIView):
    authentication_classes = [AllowAny]

    def get(self, request, token):
        try:
            payload = jwt.decode(token, key=env("TOKEN_SECRET"), algorithms=["HS256"])
            user_id = payload["user_id"]
            new_email = payload["new_email"]

            user = User.objects.get(id=user_id)
            user.email = new_email
            user.save()

            return Response(
                {"detail": "Email successfully updated."}, status=status.HTTP_200_OK
            )

        except Exception:
            return Response(
                {"detail": "Invalid or expired token."},
                status=status.HTTP_400_BAD_REQUEST,
            )


class SendEmail(APIView):
    permission_classes = [AllowAny]

    @rate_limit(limit=2, timeout=300)
    def post(self, request):
        first_name = request.data["first_name"]
        last_name = request.data["last_name"]
        email = request.data["email"]
        phone = request.data["phone"]
        message = request.data["message"]

        send_test_email(first_name, last_name, email, phone, message)

        return Response({"message": "Successfully sent test email."})


class UserRegister(CreateAPIView):
    """
    Create a new user.
    """

    permission_classes = [AllowAny]
    serializer_class = UserSerializer

    def perform_create(self, serializer):
        email = self.request.data["email"]

        if User.objects.filter(email=email).exists():
            raise ValidationError(
                {
                    "error": "invalid_data",
                    "description": "User with this email already exists.",
                }
            )

        password = make_password(self.request.data["password"])
        serializer.save(password=password)


class UserLogin(APIView):
    """
    Login with existing user credentials.
    """

    permission_classes = [AllowAny]
    serializer_class = UserSerializer

    def post(self, request):
        username = request.data["username"]
        password = request.data["password"]

        data = create_auth_token(username=username, password=password)
        token = data.get("access_token")
        if token is None:
            return Response(
                data=data,
                status=status.HTTP_400_BAD_REQUEST,
            )

        response = Response()
        response.data = {
            "access_token": token,
            "exp": data.get("exp"),
            "user": data.get("user"),
        }
        return response


class AuthTemplateView(APIView):
    permission_classes = [AllowAny]

    def handle_auth(self, request, api_url, headers, token_field="token"):
        try:
            response = requests.get(api_url, headers=headers)
            response_data = response.json()
            if "error" in response_data:
                return Response(
                    {
                        "status": "error",
                        "message": f"Wrong {token_field} or this {token_field} is already expired.",
                        "payload": {},
                    },
                    status=status.HTTP_400_BAD_REQUEST,
                )
        except Exception:
            return Response(
                {
                    "status": "error",
                    "message": "Unexpected error occurred, contact support for more info",
                    "payload": {},
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

        email = response_data["email"].lower()
        first_name = response_data.get(
            "given_name", response_data.get("name", "").split(" ", 1)[0]
        )
        last_name = response_data.get(
            "family_name",
            response_data.get("name", "").split(" ", 1)[1]
            if len(response_data.get("name", "").split(" ", 1)) > 1
            else "",
        )

        with transaction.atomic():
            user = User.objects.filter(email=email).first()
            if user is None:
                username = create_username(email)
                new_password = secrets.token_urlsafe(16)
                password = make_password(new_password)
                user = User.objects.create_user(
                    username=username,
                    password=password,
                    email=email,
                    first_name=first_name,
                    last_name=last_name,
                )

                send_welcome_email(email, username, new_password)
            if not user.is_active:
                user.is_active = True
                user.save()

        token_data = create_auth_token(email=user.email, password=user.password)
        token = token_data.get("access_token")
        if token is None:
            return Response(
                data=token_data,
                status=status.HTTP_400_BAD_REQUEST,
            )

        return Response(
            data={
                "status": "success",
                "message": "Login Successful",
                "access_token": token,
                "exp": token_data.get("exp"),
                "user": token_data.get("user"),
            },
            status=status.HTTP_201_CREATED,
        )


class GoogleAuthView(AuthTemplateView):
    permission_classes = [AllowAny]

    def post(self, request):
        return self.handle_auth(
            request,
            "https://www.googleapis.com/oauth2/v3/userinfo",
            {"Authorization": f"Bearer {request.data.get('token')}"},
            "google token",
        )


class FacebookAuthView(AuthTemplateView):
    permission_classes = [AllowAny]

    def post(self, request):
        access_token = request.data.get("token")
        return self.handle_auth(
            request,
            f"https://graph.facebook.com/v12.0/me?fields=id,name,email&access_token={access_token}",
            {},
            "facebook token",
        )


### API ###
class UserList(APIView):
    """
    List all users.
    """

    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated, IsAdminUser]

    def get(self, request, format=None):
        users = User.objects.all()
        user_serializer = UserSerializer(users, many=True)
        return Response(user_serializer.data)


class UserDetail(APIView):
    """
    Retrieve, update or delete a user.
    """

    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    serializer_class = UserUpdateSerializer

    def get_object(self, pk):
        try:
            return User.objects.get(pk=pk)
        except User.DoesNotExist:
            raise Http404

    def get(self, request, pk, format=None):
        user = self.get_object(pk)
        self.check_object_permissions(request, user)
        user_serializer = UserUpdateSerializer(user)
        return Response(user_serializer.data)

    def put(self, request, pk, format=None):
        user = self.get_object(pk)
        self.check_object_permissions(request, user)

        if request.data["password"] == "":
            request.data["password"] = user.password
        else:
            request.data["password"] = make_password(request.data["password"])

            send_password_notification_email(email=user.email)

        user_serializer = UserUpdateSerializer(user, data=request.data)
        if user_serializer.is_valid():
            user_serializer.save()
            return Response(user_serializer.data)
        return Response(user_serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk, format=None):
        user = self.get_object(pk)
        self.check_object_permissions(request, user)
        user.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
