from django.db import models
from django.utils import timezone

from config import settings

NULLABLE = {'blank': True, 'null': True}


class Client(models.Model):
    email = models.EmailField(unique=True)
    full_name = models.CharField(max_length=100)
    comment = models.TextField(blank=True)
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, **NULLABLE, verbose_name='Автор')

    def __str__(self):
        return self.full_name


class Message(models.Model):
    subject = models.CharField(max_length=255)
    body = models.TextField()
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, **NULLABLE, verbose_name='Автор')

    def __str__(self):
        return self.subject


class Mailing(models.Model):
    FIRST_SEND_CHOICES = (
        ('now', 'Сразу'),
        ('scheduled', 'Запланировать'),
    )
    FREQUENCY_CHOICES = (
        ('daily', 'Раз в день'),
        ('weekly', 'Раз в неделю'),
        ('monthly', 'Раз в месяц'),
    )
    STATUS_CHOICES = (
        ('created', 'Создана'),
        ('running', 'Запущена'),
        ('completed', 'Завершена'),
    )

    first_send = models.DateTimeField(default=timezone.now)
    frequency = models.CharField(max_length=10, choices=FREQUENCY_CHOICES)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='created')
    message = models.ForeignKey(Message, on_delete=models.CASCADE)  # Many-to-One связь с моделью Message
    clients = models.ManyToManyField(Client)  # Many-to-Many связь с моделью Client
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, **NULLABLE, verbose_name='Автор')

    def __str__(self):
        return f"Mailing #{self.id}"


class SendingAttempt(models.Model):
    STATUS_CHOICES = (
        ('success', 'Успешно'),
        ('failure', 'Не успешно'),
    )

    mailing = models.ForeignKey(Mailing, on_delete=models.CASCADE)  # Связь с моделью Mailing
    timestamp = models.DateTimeField(default=timezone.now)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES)
    server_response = models.TextField(blank=True)

    def __str__(self):
        return f"Attempt for Mailing #{self.mailing_id}"
