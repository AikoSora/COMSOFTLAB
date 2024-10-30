from django.db import models

from typing import TYPE_CHECKING


class Server(models.Model):

    class ServerList(models.TextChoices):
        GOOGLE = 'imap.gmail.com', 'Google'
        MAILRU = 'imap.mail.ru', 'Mail.ru'
        YANDEX = 'imap.yandex.ru', 'Yandex'

    if TYPE_CHECKING:
        username: str
        password: str
        server: ServerList

    else:
        username = models.CharField(
            verbose_name='Имя пользователя',
            max_length=256,
        )
        # Username imap server

        password = models.CharField(
            verbose_name='Пароль пользователя',
            max_length=100,
        )
        # Password imap server

        server = models.CharField(
            verbose_name='IMAP Сервер',
            choices=ServerList.choices,
            max_length=14,
        )
        # Imap server

    def __str__(self):
        return f'{self.username} | {self.server.capitalize()}'


__all__ = (
    'Server',
)
