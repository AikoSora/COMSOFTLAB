from aioimaplib.aioimaplib import IMAP4_SSL

from mail.crud import get_servers
from mail.models import Server
from mail.schema import RawMailsSchema

from typing import TYPE_CHECKING

from base64 import b64decode
from shlex import split

import logging

if TYPE_CHECKING:
    from typing import AsyncGenerator


def b64padanddecode(b):
    """
    Decode unpadded base64 data
    """

    b += (-len(b) % 4) * '='

    return b64decode(
        s=b,
        altchars='+,',
        validate=True,
    ).decode('utf-16-be')


def imaputf7decode(s):
    """
    Decode a string encoded according to RFC2060 aka IMAP UTF7.

    Minimal validation of input, only works with trusted data
    """

    lst = s.split('&')
    out = lst[0]

    for e in lst[1:]:
        u , a = e.split('-',1)
        if u == '':
            out += '&'
        else:
            out += b64padanddecode(u)

        out += a

    return out


async def get_imap_servers() -> list[IMAP4_SSL]:
    '''
    Function to get a imap servers

    :return list[IMAP4_SSL]:
    '''

    server_list: list[IMAP4_SSL] = []

    async for server in get_servers():
        imap_client = IMAP4_SSL(host=server.server)

        await imap_client.wait_hello_from_server()

        response = await imap_client.login(server.username, server.password)

        if response.result != 'OK':
            logging.info(f'[LOGIN]: {response}')
            continue

        server_list.append(imap_client)

    return server_list


async def get_all_folders(server: IMAP4_SSL) -> 'AsyncGenerator[str]':
    '''
    Function to get all folders in account

    :param IMAP4_SSL:
    :return AsyncioGenerator[str]: Folders
    '''

    result, raw_folders = await server.list('""', '*')

    if result == 'OK':

        for folder in raw_folders:

            if server.host in [
                Server.ServerList.GOOGLE,
                Server.ServerList.YANDEX,
            ]:
                folder = split(folder.decode())[-1]

            else:
                folder = split(imaputf7decode(folder.decode()))[-1]

            if folder.lower().replace('.', '') in [
                'done', 'success', 'completed'
            ]:
                break

            yield folder

    else:
        logging.info(f'[LIST {server.host}]: {result} | {raw_folders}')


async def get_all_mails() -> 'AsyncGenerator[RawMailsSchema]':
    '''
    Function to get all mails in all folders

    :returns AsyncGenerator[RawMailsSchema]: Mail object
    '''

    server_list: list[IMAP4_SSL] = await get_imap_servers()

    for server in server_list:

        async for folder in get_all_folders(server):
            result, data = await server.select(folder)

            if result != 'OK':
                logging.info(f'[SELECT {server.host}]: ({folder}) {result} | {data}')
                continue

            result, data = await server.search('ALL')

            if result != 'OK':
                logging.info(f'[SEARCH {server.host}]: ALL {result} | {data}')
                continue

            for id in data[0].decode('utf-8').split():
                yield RawMailsSchema(
                    id=int(id),
                    folder=folder,
                    server=server,
                )


__all__ = (
    'get_imap_servers',
    'get_all_mails',
)
