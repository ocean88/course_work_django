from django.core.management.base import BaseCommand
from django.utils import timezone
from mainapp.models import Mailing, SendingAttempt
from django.core.mail import send_mail
from django.conf import settings
import smtplib


class Command(BaseCommand):
    help = "Ручная отправка рассылок"

    def handle(self, *args, **options):
        zone = timezone.get_current_timezone()
        current_datetime = timezone.now().astimezone(zone)

        mailings = Mailing.objects.filter(first_send__lte=current_datetime, status='created')

        for mailing in mailings:
            for client in mailing.clients.all():
                try:
                    send_mail(
                        subject=mailing.message.subject,
                        message=mailing.message.body,
                        from_email=settings.EMAIL_HOST_USER,
                        recipient_list=[client.email],
                        fail_silently=False  # Не игнорировать ошибки при отправке
                    )
                    # Заносим информацию об успешной попытке в базу данных
                    attempt = SendingAttempt.objects.create(
                        mailing=mailing,
                        status='success',
                        server_response='Message sent successfully at ' + str(timezone.now())
                    )
                    attempt.save()
                except smtplib.SMTPException as e:
                    # Заносим информацию о неудачной попытке в базу данных
                    attempt = SendingAttempt.objects.create(
                        mailing=mailing,
                        status='failure',
                        server_response='Failed to send message: ' + str(e)
                    )
                    attempt.save()

            # Обновляем статус рассылки после отправки писем
            mailing.status = 'running'
            mailing.save()

        self.stdout.write(self.style.SUCCESS('Рассылки успешно отправлены'))
