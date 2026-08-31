import secrets

from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    """扩展用户模型"""
    phone = models.CharField(max_length=20, blank=True, default="", verbose_name="手机号")
    avatar = models.CharField(max_length=255, blank=True, default="", verbose_name="头像URL")

    class Meta:
        verbose_name = "用户"
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.username


class Token(models.Model):
    """API Token"""
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="tokens",
        verbose_name="用户",
    )
    key = models.CharField(max_length=64, unique=True, verbose_name="Token Key")
    created = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")

    class Meta:
        verbose_name = "Token"
        verbose_name_plural = verbose_name

    def save(self, *args, **kwargs):
        if not self.key:
            self.key = secrets.token_hex(32)
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.user.username} - {self.key[:8]}..."
