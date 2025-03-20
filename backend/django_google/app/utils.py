from django.core.cache import cache
from django.contrib.auth.models import User
from django.http import JsonResponse
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.core.mail import send_mail

import logging
import secrets
import environ
import datetime
import jwt

from app.serializers import UserSerializer

env = environ.Env()


def generate_email_change_token(user, new_email):
    now = datetime.datetime.now(datetime.timezone.utc)
    exp = int((now + datetime.timedelta(minutes=60)).timestamp())

    payload = {"user_id": user.id, "new_email": new_email, "exp": exp}
    token = jwt.encode(payload, key=env("TOKEN_SECRET"), algorithm="HS256")

    return token


def send_confirmation_email(user, token):
    try:
        subject = "Confirm your new email"

        html_message = render_to_string(
            "password_change_notification.html",
            {
                "token": token,
            },
        )
        plain_message = strip_tags(html_message)

        send_mail(
            subject=subject,
            message=plain_message,
            html_message=html_message,
            from_email=env("EMAIL_USER"),
            recipient_list=[user.email],
            fail_silently=True,
        )

    except Exception:
        logging.warning(
            "An error occurred while sending email, contact support for more info"
        )


## Create token for base login and auth template
def create_auth_token(password, email=None, username=None):
    try:
        if username is None:
            user = User.objects.get(email=email)
        elif email is None:
            user = User.objects.get(username=username)
    except User.DoesNotExist:
        return {"status": "invalid_data", "message": "Incorrect username or password."}

    if email is None and not user.check_password(password):
        return {"status": "invalid_data", "message": "Incorrect username or password."}

    now = datetime.datetime.now(datetime.timezone.utc)
    iat = int(now.timestamp())
    exp = int((now + datetime.timedelta(minutes=env.int("TOKEN_EXP_MIN"))).timestamp())

    payload = {
        "id": user.id,
        "email": user.email,
        "exp": exp,
        "iat": iat,
    }

    token = jwt.encode(payload, key=env("TOKEN_SECRET"), algorithm="HS256")
    user_serializer = UserSerializer(user)

    return {
        "access_token": token,
        "exp": datetime.datetime.fromtimestamp(exp),
        "user": user_serializer.data,
    }


## Create username from email
def create_username(email):
    try:
        email_split = email.split("@")
        email_part = email_split[0]
        username = f"{email_part.lower()}_{secrets.token_hex(5)}"
        return username
    except Exception as e:
        raise Exception("Error while creating a new username") from e


## Send welcome email to users that logged in using Base, Google or Facebook auth
def send_welcome_email(email, username, password):
    try:
        subject = "Welcome!"
        html_message = render_to_string(
            "welcome_email.html",
            {
                "password": password,
                "username": username,
            },
        )
        plain_message = strip_tags(html_message)

        send_mail(
            subject=subject,
            message=plain_message,
            html_message=html_message,
            from_email=env("EMAIL_USER"),
            recipient_list=[email],
            fail_silently=True,
        )

    except Exception:
        logging.warning(
            "An error occurred while sending email, contact support for more info"
        )


## Send Test email
def send_test_email(first_name, last_name, email, phone, message):
    subject = "Test Email."
    html_message = render_to_string(
        "test_email.html",
        {
            "first_name": first_name,
            "last_name": last_name,
            "email": email,
            "phone": phone,
            "message": message,
        },
    )

    plain_message = strip_tags(html_message)

    send_mail(
        subject=subject,
        message=plain_message,
        html_message=html_message,
        from_email=env("EMAIL_USER"),
        recipient_list=["fd.melnik@yandex.ru"],
        fail_silently=True,
    )


## Send password notification email
def send_password_notification_email(email):
    subject = "Account password changed"
    html_message = render_to_string("password_change_notification.html")

    plain_message = strip_tags(html_message)

    send_mail(
        subject=subject,
        message=plain_message,
        html_message=html_message,
        from_email=env("EMAIL_USER"),
        recipient_list=[email],
        fail_silently=True,
    )


## Rate limit decorator
def rate_limit(limit=10, timeout=300):
    def decorator(view_func):
        def wrapped_view(self, request, *args, **kwargs):
            ip = request.META.get("REMOTE_ADDR")
            key = f"rate_limit_{ip}"

            request_count = cache.get(key, 0)
            if request_count >= limit:
                return JsonResponse({"error": "Bad Request."}, status=400)

            cache.set(key, request_count + 1, timeout)
            return view_func(self, request, *args, **kwargs)

        return wrapped_view

    return decorator
