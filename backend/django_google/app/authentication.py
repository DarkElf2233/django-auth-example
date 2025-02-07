from django.contrib.auth.models import User
from rest_framework.authentication import BaseAuthentication
from rest_framework.exceptions import AuthenticationFailed

import environ
import jwt

env = environ.Env()


class JWTAuthentication(BaseAuthentication):
    def authenticate(self, request):
        token = request.COOKIES.get('access_token')

        if not token:
            return None

        try:
            payload = jwt.decode(token, key=env('TOKEN_SECRET'), algorithms=['HS256'])
            user = User.objects.get(id=payload['id'])
        except jwt.ExpiredSignatureError:
            raise AuthenticationFailed('Invalid user credentials.')
        except (jwt.DecodeError, User.DoesNotExist):
            raise AuthenticationFailed('Invalid user credentials.')

        return (user, None)