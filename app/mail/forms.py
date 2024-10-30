from django import forms

from .models import Server


class ServerForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput)

    class Meta:
        model = Server


__all__ = (
    'ServerForm',
)
