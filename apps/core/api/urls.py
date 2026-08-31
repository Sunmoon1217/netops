from django.urls import path

from . import auth

urlpatterns = [
    path("auth/login/", auth.login, name="login"),
    path("auth/logout/", auth.logout, name="logout"),
    path("me/", auth.me, name="me"),
]
