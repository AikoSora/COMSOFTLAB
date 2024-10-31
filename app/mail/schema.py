from .schemas import BaseSchema

from aioimaplib.aioimaplib import IMAP4_SSL


class RawMailsSchema(BaseSchema):
    id: int
    folder: str
    server: IMAP4_SSL


__all__ = (
    'RawMailsSchema',
)
