from mail.models import Server

from typing import TYPE_CHECKING


if TYPE_CHECKING:
    from typing import AsyncGenerator


async def get_servers() -> 'AsyncGenerator[Server]':
    '''
    Get servers list

    :return: QuerySet[Server]
    '''

    async for query in Server.objects.all():
        yield query


__all__ = (
    'get_servers',
)
