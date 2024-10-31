from django.db import models

from .mails import Mail

from typing import TYPE_CHECKING


class Attachment(models.Model):

    if TYPE_CHECKING:
        from pathlib import Path

        mail: Mail
        file: Path

    else:
        mail = models.ForeignKey(Mail, on_delete=models.CASCADE, related_name='attachments')

        file = models.FileField()

    def __str__(self):
        return f'{self.mail} | {self.file.name}'


__all__ = (
    'Attachment',
)
