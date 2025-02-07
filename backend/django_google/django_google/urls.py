from django.contrib import admin
from django.urls import path
from app import views

urlpatterns = [
    path('admin/', admin.site.urls),

    path("auth/google/login/", views.GoogleAuthView.as_view(), name="google_login"),
    path("auth/facebook/login/", views.FacebookAuthView.as_view(), name="facebook_login"),

    path("auth/base/login/", views.UserLogin.as_view(), name="base_login"),
    path("auth/base/register/", views.UserRegister.as_view(), name="base_login"),

    path("auth/users/", views.UserList.as_view(), name="user_list"),
]
