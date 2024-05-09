from django.urls import path
from mainapp.apps import MainappConfig
from mainapp.views import (main_index, mailing_list, mailing_detail, create_mailing, edit_mailing, delete_mailing,
                           create_client, edit_client, delete_client, create_message, message_detail, edit_message,
                           delete_message, send_mailing)


app_name = MainappConfig.name

urlpatterns = [
    path('', main_index, name='index'),
    path('mailing/', mailing_list, name='mailing_list'),
    path('mailing/<int:pk>/', mailing_detail, name='mailing_detail'),
    path('mailing/new/', create_mailing, name='create_mailing'),
    path('mailing/<int:pk>/edit/', edit_mailing, name='edit_mailing'),
    path('mailing/<int:pk>/delete/', delete_mailing, name='delete_mailing'),
    path('client/new/', create_client, name='create_client'),
    path('client/<int:pk>/edit/', edit_client, name='edit_client'),
    path('client/<int:pk>/delete/', delete_client, name='delete_client'),
    path('message/new/', create_message, name='create_message'),
    path('message/<int:pk>/', message_detail, name='message_detail'),
    path('message/<int:pk>/edit/', edit_message, name='edit_message'),
    path('message/<int:pk>/delete/', delete_message, name='delete_message'),
    path('send-mailing-confirmation/', send_mailing, name='send_mailing_confirmation'),
]