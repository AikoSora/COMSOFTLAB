from django.db import models

from .mails import Mail

from typing import TYPE_CHECKING


class Attachment(models.Model):

    if TYPE_CHECKING:
        from pathlib import Path

        mail: Mail
        file: str

    else:
        mail = models.ForeignKey(Mail, on_delete=models.CASCADE, related_name='attachments')

        file = models.TextField(verbose_name='URL файла')

    def __str__(self):
        return f'{self.mail} | {self.file}'


__all__ = (
    'Attachment',
)
