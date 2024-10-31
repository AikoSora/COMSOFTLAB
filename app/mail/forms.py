from django import forms

from .models import Server


class ServerForm(forms.ModelForm):
    password = forms.CharField(
        label='Пароль пользователя',
        widget=forms.PasswordInput,
    )

    class Meta:
        model = Server
        fields = '__all__'


__all__ = (
    'ServerForm',
)
