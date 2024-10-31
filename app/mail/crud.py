from mail.models import Server, Folder, Mail, Attachment

from typing import TYPE_CHECKING


if TYPE_CHECKING:
    from typing import AsyncGenerator
    from pathlib import Path
    from datetime import datetime


async def get_servers() -> 'AsyncGenerator[Server]':
    '''
    Get servers list

    :return: AsyncGenerator[Server]
    '''

    async for query in Server.objects.all():
        yield query


async def get_server_by_host(*, host: str, **kwargs) -> Server | None:
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


async def create_attachment(*, file: 'Path', mail: Mail, **kwargs) -> Attachment:
    '''
    Function to create Attachment object

    :param file: Path
    :param mail: Mail object

    :return Attachment:
    '''

    return await Attachment.objects.acreate(
        mail=mail,
        file=file,
    )


async def create_mail(
        *,
        mail_id: int,
        folder: Folder,
        sender: str,
        text: str = None,
        theme: str = None,
        sending_date: 'datetime' = None,
        receiving_date: 'datetime' = None,
        **kwargs,
) -> Mail:
    '''
    Function to create Mail object

    :param mail_id: Mail id in server
    :param folder: Folder object
    :param sender: Sender email adress
    :param text: Message text
    :param theme: Message theme (default None)
    :param sending_date: Sending date
    :param receiving_date: Receiving date

    :return Mail:
    '''

    return await Mail.objects.acreate(
        mail_id=mail_id,
        folder=folder,
        sender=sender,
        theme=theme,
        sending_date=sending_date,
        receiving_date=receiving_date,
        text=text,
    )


async def get_mail_by_id(*, mail_id: int, **kwargs) -> Mail | None:
    '''
    Function to get a mail by mail_id

    :param mail_id: int

    :return Mail: Mail object
    '''

    return await Mail.objects.filter(mail_id=mail_id).afirst()


async def get_mail_attachments(*, mail: Mail, **kwargs) -> 'AsyncGenerator[Attachment]':
    '''
    Get mail attachment list

    :return: AsyncGenerator[Attachment]
    '''

    async for attachment in mail.attachments.all():
        yield attachment


async def mails_count(*args, **kwargs) -> int:
    '''
    Function to get count mails

    :return int:
    '''

    return await Mail.objects.acount()


__all__ = (
    'get_servers',
    'get_or_create_folder',
    'get_server_by_host',
    'create_attachment',
    'create_mail',
    'get_mail_by_id',
    'get_mail_attachments',
    'mails_count',
)
