from django.db import models

from .folders import Folder

from typing import TYPE_CHECKING


class Mail(models.Model):

    if TYPE_CHECKING:
        from datetime import datetime

        mail_id: int
        folder: Folder
        sender: str
        theme: str
        sending_date: datetime
        receiving_date: datetime
        text: str

    else:
        mail_id = models.IntegerField(verbose_name='ID Сообщения на сервере')

        folder = models.ForeignKey(Folder, on_delete=models.CASCADE, related_name='mails')

        sender = models.TextField(verbose_name='Отправитель')

        theme = models.TextField(
            verbose_name='Тема сообщения',
            default=None,
            null=True,
            blank=True,
        )

        sending_date = models.DateTimeField(verbose_name='Дата отправки')

        receiving_date = models.DateTimeField(verbose_name='Дата получения')

        text = models.TextField(
            verbose_name='Текст сообщения',
            default=None,
            null=True,
            blank=True,
        )

    def __str__(self):
        return f'{self.mail_id} | {self.folder}'


__all__ = (
    'Mail',
)
