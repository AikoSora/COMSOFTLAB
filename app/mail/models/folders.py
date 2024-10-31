from django.db import models

from .servers import Server

from typing import TYPE_CHECKING


class Folder(models.Model):

    if TYPE_CHECKING:
        name: str
        server: Server

    else:
        name = models.TextField(verbose_name='Название')
        server = models.ForeignKey(Server, on_delete=models.CASCADE, related_name='folders')

    def __str__(self):
        return f'{self.name} | {self.server}'


__all__ = (
    'Folder',
)
