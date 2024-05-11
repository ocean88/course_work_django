import smtplib

from django.shortcuts import render, redirect, get_object_or_404
from django.conf import settings
from django.utils import timezone

from blog.models import Blog
from .models import Mailing, Client, Message, SendingAttempt
from .forms import MailingForm, ClientForm, MessageForm
from django.core.mail import send_mail
import pytz
from django.contrib.auth.decorators import login_required
from django.views.decorators.cache import cache_page
from .services import get_model_from_cache


@login_required
def send_mailing(request):
    zone = pytz.timezone(settings.TIME_ZONE)
    current_datetime = timezone.now().astimezone(zone)

    mailings = Mailing.objects.filter(owner=request.user, first_send__lte=current_datetime, status='created')

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


@cache_page(60 * 15)  # Cache for 15 minutes
@login_required
def main_index(request):
    if request.user.is_staff or request.user.is_superuser:
        clients = get_model_from_cache(Client)
        mailings = get_model_from_cache(Mailing)
        messages = get_model_from_cache(Message)
        blogs = get_model_from_cache(Blog)
    else:
        clients = get_model_from_cache(Client).filter(owner=request.user)
        mailings = get_model_from_cache(Mailing).filter(owner=request.user)
        messages = get_model_from_cache(Message).filter(owner=request.user)
        blogs = get_model_from_cache(Blog)

    context = {
        'clients': clients,
        'mailings': mailings,
        'messages': messages,
        'blogs': blogs
    }

    return render(request, 'mainapp/index.html', context)


@login_required
def create_client(request):
    if request.method == 'POST':
        form = ClientForm(request.POST)
        if form.is_valid():
            client = form.save(commit=False)
            client.owner = request.user  # Associate the client with the current user
            client.save()
            return redirect('mainapp:index')
    else:
        form = ClientForm()
    return render(request, 'mainapp/create_client.html', {'form': form})


@login_required
def edit_client(request, pk):
    client = get_object_or_404(Client, pk=pk, owner=request.user)  # Ensure the client belongs to the current user
    if request.method == 'POST':
        form = ClientForm(request.POST, instance=client)
        if form.is_valid():
            form.save()
            return redirect('mainapp:index')
    else:
        form = ClientForm(instance=client)
    return render(request, 'mainapp/edit_client.html', {'form': form})


@login_required
def delete_client(request, pk):
    client = get_object_or_404(Client, pk=pk, owner=request.user)  # Ensure the client belongs to the current user
    if request.method == 'POST':
        client.delete()
        return redirect('mainapp:create_client')
    return render(request, 'mainapp/delete_client.html', {'client': client})


def mailing_list(request):
    mailings = Mailing.objects.all()
    return render(request, 'mainapp/mailing_list.html', {'mailings': mailings})


@login_required
def mailing_detail(request, pk):
    mailing = get_object_or_404(Mailing, pk=pk, owner=request.user)  # Ensure the mailing belongs to the current user
    return render(request, 'mainapp/mailing_detail.html', {'mailing': mailing})


@login_required
def create_mailing(request):
    if request.method == 'POST':
        form = MailingForm(request.POST, user=request.user)
        if form.is_valid():
            mailing = form.save(commit=False)
            mailing.owner = request.user
            mailing.save()
            return redirect('mainapp:index')  # Update with your actual redirect URL
    else:
        form = MailingForm(user=request.user)

    return render(request, 'mainapp/mailing_edit.html', {'form': form})


@login_required
def edit_mailing(request, pk):
    mailing = get_object_or_404(Mailing, pk=pk, owner=request.user)  # Ensure the mailing belongs to the current user
    if request.method == 'POST':
        form = MailingForm(request.POST, instance=mailing)
        if form.is_valid():
            form.save()
            return redirect('mainapp:mailing_detail', pk=mailing.pk)
    else:
        form = MailingForm(instance=mailing)
    return render(request, 'mainapp/mailing_edit.html', {'form': form})


@login_required
def delete_mailing(request, pk):
    mailing = get_object_or_404(Mailing, pk=pk, owner=request.user)  # Ensure the mailing belongs to the current user
    mailing.delete()
    return redirect('mainapp:index')


@login_required
def create_message(request):
    if request.method == 'POST':
        form = MessageForm(request.POST)
        if form.is_valid():
            message = form.save(commit=False)
            message.owner = request.user  # Associate the message with the current user
            message.save()
            return redirect('mainapp:message_detail', pk=message.pk)
    else:
        form = MessageForm()
    return render(request, 'mainapp/message_form.html', {'form': form})


def message_detail(request, pk):
    message = get_object_or_404(Message, pk=pk)
    return render(request, 'mainapp/message_detail.html', {'message': message})


@login_required
def edit_message(request, pk):
    message = get_object_or_404(Message, pk=pk, owner=request.user)  # Ensure the message belongs to the current user
    if request.method == 'POST':
        form = MessageForm(request.POST, instance=message)
        if form.is_valid():
            form.save()
            return redirect('mainapp:index')
    else:
        form = MessageForm(instance=message)
    return render(request, 'mainapp/message_edit.html', {'form': form})


@login_required
def delete_message(request, pk):
    message = get_object_or_404(Message, pk=pk, owner=request.user)  # Ensure the message belongs to the current user
    if request.method == 'POST':
        message.delete()
        return redirect('mainapp:index')
    return render(request, 'mainapp/message_confirm_delete.html', {'message': message})
