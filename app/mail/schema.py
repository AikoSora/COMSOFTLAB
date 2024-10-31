from schemas import BaseSchema

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from aioimaplib.aioimaplib import IMAP4_SSL


class RawMailsSchema(BaseSchema):
    id: int
    folder: str
    server: 'IMAP4_SSL'


__all__ = (
    'RawMailsSchema',
)
