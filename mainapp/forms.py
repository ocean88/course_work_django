from django.utils import timezone
from django.contrib.auth import get_user_model
from django import forms
from .models import Mailing, Client, Message


class ClientForm(forms.ModelForm):
    class Meta:
        model = Client
        fields = ['email', 'full_name', 'comment']
        labels = {
            'email': 'Email',
            'full_name': 'Full Name',
            'comment': 'Comment (optional)',
        }


User = get_user_model()


class MailingForm(forms.ModelForm):
    class Meta:
        model = Mailing
        fields = ['first_send', 'frequency', 'message', 'clients']

    def __init__(self, *args, user=None, **kwargs):
        super().__init__(*args, **kwargs)
        if user and not (user.is_staff or user.is_superuser):
            self.fields['clients'].queryset = Client.objects.filter(owner=user)
            self.fields['message'].queryset = Message.objects.filter(owner=user)
        self.fields['first_send'].widget.attrs['min'] = timezone.now().strftime('%Y-%m-%dT%H:%M')  # Set the minimum value for the first_send field


class MessageForm(forms.ModelForm):
    class Meta:
        model = Message
        fields = ['subject', 'body']