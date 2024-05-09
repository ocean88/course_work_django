from django.contrib.auth.views import LogoutView
from django.urls import path
from users.apps import UsersConfig
from users.views import UserCreateView, RegisterMessageView, CustomLoginView, email_verification, PasswordResetView

app_name = UsersConfig.name

urlpatterns = [
    path('login/', CustomLoginView.as_view(template_name='login.html'), name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('register/', UserCreateView.as_view(), name='register'),
    path('email-confirm/<str:token>/', email_verification, name='confirm_register'),
    path('register/message/', RegisterMessageView.as_view(), name='SuccessRegister'),
    path('password_reset/', PasswordResetView.as_view(), name='password_reset'),
]

