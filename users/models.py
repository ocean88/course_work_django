from django.contrib.auth.models import AbstractUser
from django.db import models


# Create your models here.
NULLABLE = {'blank': True, 'null': True}


class User(AbstractUser):
    username = None
    email = models.EmailField(unique=True, verbose_name='Email')
    avatar = models.ImageField(upload_to='avatars/', verbose_name='Аватар', help_text='Загрузите аватар', **NULLABLE)
    token = models.CharField(max_length=100, verbose_name="Код верификации", **NULLABLE)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'

    def __str__(self):
        return self.email
