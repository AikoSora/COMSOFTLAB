from mail.models import Server, Folder

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


async def get_server_by_host(*, host: str, **kwargs) -> Server:
    '''
    Function to get a server by host

    :param host: str

    :return Server: Server object
    '''

    return await Server.objects.filter(server=host).afirst()


async def get_or_create_folder(*, name: str, server: Server, **kwargs) -> Folder:
    '''
    Function to get or create folder

    :param name: str
    :param server: Server object

    :return Folder:
    '''

    folder = await Folder.objects.filter(name=name, server=server).afirst()

    if folder is None:
        folder = await Folder.objects.acreate(
            name=name,
            server=server,
        )

    return folder


__all__ = (
    'get_servers',
    'get_or_create_folder',
    'get_server_by_host',
)
