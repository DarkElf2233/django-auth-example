from django.db import transaction
from django.contrib.auth.models import User
from django.contrib.auth.hashers import make_password

from rest_framework import status
from rest_framework.generics import CreateAPIView
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny, IsAuthenticated, IsAdminUser
from rest_framework.response import Response
from rest_framework.exceptions import ValidationError

import requests
import datetime
import environ
import jwt
import secrets

from app.serializers import UserSerializer
from app.authentication import JWTAuthentication

env = environ.Env()


### AUTH ###
def create_token(email, password):
    try:
        user = User.objects.get(email=email)
    except User.DoesNotExist:
        return {
            'status': 'invalid_data',
            'message': 'Incorrect email or password.'
        }

    if not user.check_password(password):
        if user.check_password(make_password(password)):
            return {
                'status': 'invalid_data',
                'message': 'Incorrect email or password.'
            }

    now = datetime.datetime.now(datetime.timezone.utc)
    iat = int(now.timestamp())
    exp = int((now + datetime.timedelta(minutes=env.int('TOKEN_EXP_MIN'))).timestamp())

    payload = {
        'id': user.id,
        'email': user.email,
        'exp': exp,
        'iat': iat,
    }

    token = jwt.encode(payload, key=env('TOKEN_SECRET'), algorithm='HS256')
    user_serializer = UserSerializer(user)

    return {
        'access_token': token,
        'exp': datetime.datetime.fromtimestamp(exp),
        'user': user_serializer.data
    }


def create_username(email):
    try:
        email_split = email.split("@")
        email_part = email_split[0]
        username = f'{email_part.lower()}_{secrets.token_hex(5)}'
        return username
    except Exception as e:
        raise Exception("Error while creating a new username") from e


class UserRegister(CreateAPIView):
    """
    Create a new user.
    """
    permission_classes = [AllowAny]
    serializer_class = UserSerializer

    def perform_create(self, serializer):
        email = self.request.data['email']

        if User.objects.filter(email=email).exists():
            raise ValidationError({
                'error': 'invalid_data',
                'description': 'User with this email already exists.'
            })

        password = make_password(self.request.data['password'])
        serializer.save(password=password)


class UserLogin(APIView):
    """
    Login with existing user credentials.
    """
    permission_classes = [AllowAny]
    serializer_class = UserSerializer

    def post(self, request):
        email = request.data['email']
        password = request.data['password']

        data = create_token(email, password)
        token = data.get('access_token')
        if token is None:
            return Response(
                data=data,
                status=status.HTTP_400_BAD_REQUEST,
            )

        response = Response()
        response.data = {
            'access_token': token,
            'exp': data.get('exp'),
            'user': data.get('user')
        }
        return response


class AuthTemplateView(APIView):
    permission_classes = [AllowAny]

    def handle_auth(self, request, api_url, headers, token_field='token'):
        try:
            response = requests.get(api_url, headers=headers)
            response_data = response.json()
            if 'error' in response_data:
                return Response({
                    "status": "error",
                    "message": f"Wrong {token_field} or this {token_field} is already expired.",
                    "payload": {}
                }, status=status.HTTP_400_BAD_REQUEST)
        except Exception:
            return Response({
                "status": "error",
                "message": "Unexpected error occurred, contact support for more info",
                "payload": {}
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        email = response_data['email'].lower()
        first_name = response_data.get("given_name", response_data.get("name", "").split(' ', 1)[0])
        last_name = response_data.get("family_name", response_data.get("name", "").split(' ', 1)[1] if len(response_data.get("name", "").split(' ', 1)) > 1 else "")

        with transaction.atomic():
            user = User.objects.filter(email=email).first()
            if user is None:
                username = create_username(email)
                new_password = secrets.token_urlsafe(16)
                password = make_password(new_password)
                user = User.objects.create_user(
                    username=username, password=password, email=email, first_name=first_name, last_name=last_name)
            if not user.is_active:
                user.is_active = True
                user.save()

        token_data = create_token(user.email, user.password)
        token = token_data.get('access_token')
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
                "exp": token_data.get('exp'),
                "user": token_data.get('user'),
            },
            status=status.HTTP_201_CREATED,
        )


class GoogleAuthView(AuthTemplateView):
    permission_classes = [AllowAny]

    def post(self, request):
        return self.handle_auth(
            request,
            'https://www.googleapis.com/oauth2/v3/userinfo',
            {"Authorization": f"Bearer {request.data.get('token')}"},
            'google token'
        )


class FacebookAuthView(AuthTemplateView):
    permission_classes = [AllowAny]

    def post(self, request):
        access_token = request.data.get('token')
        return self.handle_auth(
            request,
            f'https://graph.facebook.com/v12.0/me?fields=id,name,email&access_token={access_token}',
            {},
            'facebook token'
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
