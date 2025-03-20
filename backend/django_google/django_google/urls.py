from django.contrib import admin
from django.urls import path
from app import views

urlpatterns = [
    path("admin/", admin.site.urls),
    path("auth/google/login/", views.GoogleAuthView.as_view(), name="google_login"),
    path(
        "auth/facebook/login/", views.FacebookAuthView.as_view(), name="facebook_login"
    ),
    path("auth/base/login/", views.UserLogin.as_view(), name="base_login"),
    path("auth/base/register/", views.UserRegister.as_view(), name="base_login"),
    path("auth/users/", views.UserList.as_view(), name="user_list"),
    path("auth/users/<int:pk>", views.UserDetail.as_view(), name="user_detail"),
    path("auth/change-email/", views.ChangeEmailView.as_view(), name="change-email"),
    path(
        "auth/confirm-email/<str:token>/",
        views.ConfirmEmailView.as_view(),
        name="confirm-email",
    ),
    path("contactus/", views.SendEmail().as_view(), name="send_email"),
]
