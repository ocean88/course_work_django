from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from users.models import User
from django import forms


class LoginCustomForm(AuthenticationForm):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            field.widget.attrs['class'] = 'form-control'


class UserRegisterForm(UserCreationForm):

    class Meta:
        model = User
        fields = ('email', 'password1', 'password2')


class PasswordResetForm(forms.Form):
    email = forms.EmailField(label='Email', max_length=100, widget=forms.EmailInput(attrs={'class': 'form-control'}))

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            field.widget.attrs['class'] = 'form-control'