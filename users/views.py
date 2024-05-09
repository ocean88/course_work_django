import random
from django.contrib.auth.views import LoginView
from django.core.mail import send_mail
from django.urls import reverse_lazy, reverse
from django.views.generic import CreateView, TemplateView, FormView
from users.forms import UserRegisterForm, PasswordResetForm
from users.models import User
from config.settings import EMAIL_HOST_USER
from django.shortcuts import get_object_or_404, redirect, render
import secrets


class UserCreateView(CreateView):
    model = User
    form_class = UserRegisterForm
    success_url = reverse_lazy('users:SuccessRegister')

    def form_valid(self, form):
        user = form.save()
        user.is_active = False
        token = secrets.token_hex(16)
        user.token = token
        user.save()
        host = self.request.get_host()
        url = f'http://{host}/users/email-confirm/{token}/'
        print('до отправки email')
        send_mail(
            subject="Подтверждение почты",
            message=f"Для подтверждения почты перейдите по {url}",
            from_email=EMAIL_HOST_USER,
            recipient_list=[user.email],
        )
        print('После отправки email')
        return super().form_valid(form)


def email_verification(request, token):
    user = get_object_or_404(User, token=token)
    user.is_active = True
    user.save()
    return redirect(reverse("users:login"))


class RegisterMessageView(TemplateView):
    model = User
    template_name = 'users/register_message.html'


class PasswordResetView(FormView):
    template_name = 'users/reset_password.html'
    form_class = PasswordResetForm
    success_url = reverse_lazy('users:login')

    def form_valid(self, form):
        email = form.cleaned_data['email']
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            return render(self.request, 'users/reset_password.html',
                          {'form': form, 'error_message': 'User does not exist'})

        # Генерация нового пароля
        new_password = "".join([str(random.randint(0, 9)) for _ in range(10)])
        user.set_password(new_password)
        user.save()

        # Отправка сообщения с новым паролем на адрес электронной почты пользователя
        send_mail(
            'Сброс пароля',
            f'Новый пароль: {new_password}',
            EMAIL_HOST_USER,
            [user.email],
            fail_silently=False
        )

        return super().form_valid(form)


class CustomLoginView(LoginView):
    extra_context = {'password_reset_url': reverse_lazy('users:password_reset')}