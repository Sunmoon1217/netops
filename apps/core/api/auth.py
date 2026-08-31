from django.contrib.auth import authenticate
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

from core.models import Token, User


@api_view(["POST"])
@permission_classes([AllowAny])
def login(request):
    username = request.data.get("username")
    password = request.data.get("password")
    user = authenticate(username=username, password=password)
    if user is None:
        return Response({"error": "用户名或密码错误"}, status=status.HTTP_401_UNAUTHORIZED)
    token, _ = Token.objects.get_or_create(user=user)
    u = User.objects.get(pk=user.pk)
    return Response({
        "token": token.key,
        "user": {"id": u.pk, "username": u.username},
    })


@api_view(["POST"])
def logout(request):
    request.user.tokens.all().delete()
    return Response({"message": "已登出"})


@api_view(["GET"])
def me(request):
    u = User.objects.get(pk=request.user.pk)
    return Response({
        "id": u.pk,
        "username": u.username,
        "email": u.email,
        "is_staff": u.is_staff,
        "phone": u.phone,
        "avatar": u.avatar,
    })
