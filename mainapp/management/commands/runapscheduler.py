from django.core.management.base import BaseCommand
from django.utils import timezone
from mainapp.models import Mailing, SendingAttempt
from django.core.mail import send_mail
import smtplib
import logging
from django.conf import settings
from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.triggers.cron import CronTrigger
from django_apscheduler.jobstores import DjangoJobStore
from django_apscheduler.models import DjangoJobExecution
from django_apscheduler import util
from datetime import timedelta

logger = logging.getLogger(__name__)


def my_job():
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
                    fail_silently=False
                )
                attempt = SendingAttempt.objects.create(
                    mailing=mailing,
                    status='success',
                    server_response='Message sent successfully at ' + str(timezone.now())
                )
                attempt.save()
            except smtplib.SMTPException as e:
                attempt = SendingAttempt.objects.create(
                    mailing=mailing,
                    status='failure',
                    server_response='Failed to send message: ' + str(e)
                )
                attempt.save()

        mailing.status = 'running'
        mailing.save()

    print('Рассылки успешно отправлены')


@util.close_old_connections
def delete_old_job_executions(max_age=604_800):
    """
    This job deletes APScheduler job execution entries older than `max_age` from the database.
    It helps to prevent the database from filling up with old historical records that are no
    longer useful.

    :param max_age: The maximum length of time to retain historical job execution records.
                    Defaults to 7 days.
    """
    DjangoJobExecution.objects.delete_old_job_executions(max_age)


class Command(BaseCommand):
    help = "Runs APScheduler."

    def handle(self, *args, **options):
        scheduler = BlockingScheduler(timezone=settings.TIME_ZONE)
        scheduler.add_jobstore(DjangoJobStore(), "default")

        mailings = Mailing.objects.all()
        for mailing in mailings:
            trigger = None
            if mailing.frequency == 'daily':
                trigger = CronTrigger(day='1', hour='0', minute='0')
            elif mailing.frequency == 'weekly':
                trigger = CronTrigger(day_of_week='sun', hour='0', minute='0')
            elif mailing.frequency == 'monthly':
                trigger = CronTrigger(day='30',)

            if trigger:
                scheduler.add_job(
                    my_job,
                    trigger=trigger,
                    id=f"my_job_{mailing.id}",  # Уникальный id для каждой рассылки
                    max_instances=1,
                    replace_existing=True,
                )

        logger.info("Added jobs for mailings.")

        scheduler.add_job(
            delete_old_job_executions,
            trigger=CronTrigger(
                day_of_week="mon", hour="00", minute="00"
            ),  # По понедельникам в полночь, перед началом новой рабочей недели.
            id="delete_old_job_executions",
            max_instances=1,
            replace_existing=True,
        )
        logger.info(
            "Added weekly job: 'delete_old_job_executions'."
        )

        try:
            logger.info("Starting scheduler...")
            scheduler.start()
        except KeyboardInterrupt:
            logger.info("Stopping scheduler...")
            scheduler.shutdown()
            logger.info("Scheduler shut down successfully!")
