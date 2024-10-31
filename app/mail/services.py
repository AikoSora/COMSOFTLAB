from django.conf import settings

from aioimaplib.aioimaplib import IMAP4_SSL

from mail.crud import (
    get_servers,
    get_server_by_host,
    get_or_create_folder,
    create_mail,
    create_attachment,
    get_mail_by_id,
    mails_count,
)
from mail.models import Server
from mail.schema import RawMailsSchema

from typing import TYPE_CHECKING

from email import message_from_bytes
from email.utils import parsedate
from email.header import decode_header

from base64 import b64decode
from shlex import split
from bs4 import BeautifulSoup
from re import sub
from datetime import datetime
from time import mktime, time
from pathlib import Path

import logging

if TYPE_CHECKING:
    from typing import AsyncGenerator
    from email.message import Message


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
        u, a = e.split('-', 1)

        if u == '':
            out += '&'
        else:
            out += b64padanddecode(u)

        out += a

    return out


def wrapper_decode_header(data: bytes | str) -> str:
    '''
    Wrapper for decode_header function

    :param data: Bytes or str data

    :return str: Decoded text
    '''

    decoded_data = decode_header(data)

    text = decoded_data[0][0]
    encoding = decoded_data[0][1]

    if isinstance(text, bytes):
        data = text.decode(encoding)
    else:
        data = text

    return data


def parse_message_text(payload: 'Message') -> str | None:
    '''
    Function to parse message text in payload object

    :param payload: Message object

    :return str | None:
    '''

    text = None

    try:
        text = b64decode(payload.get_payload()).decode()
    except Exception as ex:
        logging.info(f'PARSEE MESSAGE TEXT] {ex}')

    return text


def parse_message_html(payload: 'Message') -> str | None:
    '''
    Function to parse message html in payload object

    :param payload: Message object

    :return str | None:
    '''

    text = None

    try:
        html = b64decode(payload.get_payload()).decode()

        parser = BeautifulSoup(html, 'html.parser')

        text = sub(' +', ' ', parser.get_text())
    except Exception as ex:
        logging.info(f'PARSEE MESSAGE HTML] {ex}')

    return text


def get_file_name(file_name: str) -> str:
    '''
    Function to get new filename

    :return str:
    '''
    from random import randint

    return ''.join(str(time()).split('.')) \
        + (str(randint(0, int(time())))) \
        + file_name


def parse_attachments(payload: 'Message', mail_id: int) -> Path:
    '''
    Function to parse message attachments in payload object

    :param payload: Message object

    :return Path:
    '''

    filename = wrapper_decode_header(payload.get_filename())
    file_absolute_media = f'files/{str(mail_id)}/'
    file_path: Path = settings.MEDIA_ROOT / file_absolute_media

    file_path.mkdir(exist_ok=True, parents=True)

    file_path = file_path / (get_file_name(file_name=filename))

    file = open(file_path, 'wb+')

    file.write(payload.get_payload(decode=True))

    file.close()

    return file_absolute_media + file_path.name


def get_mail_payload(mail_id: int, message: 'Message') -> tuple[str | None, list]:
    '''
    Function to get mail payload

    :param message: Message object
    :return tuple: Message text and attachments
    '''

    text = None
    attachments = []

    for payload in message.walk():

        if payload.get_content_maintype() == 'text':
            if payload.get_content_subtype() == 'plain':
                text = parse_message_text(payload=payload)

            elif payload.get_content_subtype() == 'html':
                text = parse_message_html(payload=payload)

        elif payload.get_content_disposition() == 'attachment':
            attachments.append(
                parse_attachments(payload=payload, mail_id=mail_id)
            )

    return text, attachments


def get_mail_data(mail_id: int, mail_data: bytes) -> tuple[datetime, str, str, str]:
    '''
    Function to get a mail data

    :param mail_data: bytes

    :return tuple[datetime, str, str, str]: Date, Sender, Theme, Text
    '''

    response = message_from_bytes(mail_data)

    date = response.get('Date', None)
    sender = response.get('Return-path', None)
    theme = response.get('Subject', None)
    message, attachments = get_mail_payload(
        message=response,
        mail_id=mail_id,
    )

    if date is not None:
        date = datetime.fromtimestamp(
            mktime(parsedate(date))
        )

    if theme is not None:
        theme = wrapper_decode_header(theme)

    return date, sender, theme, message, attachments


def search_text_in_array(array: list, text: str) -> str | None:
    '''
    Function to search text in array

    :param array: list object
    :param text: str object

    :return str | None:
    '''

    for element in array:
        if text.lower() in str(element).lower():
            return element

    return None


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


async def get_mails_count(server_list: list[IMAP4_SSL]) -> int:
    '''
    Function to get count mails in servers

    :param server_list: list[IMAP4_SSL]

    :return int: Count mails
    '''

    count = 0

    for server in server_list:

        async for folder in get_all_folders(server=server):

            result, data = await server.select(folder)

            if result != 'OK':
                logging.info(f'[SELECT {server.host}]: ({folder}) {result} | {data}')
                continue

            if data := search_text_in_array(data, 'EXISTS'):
                count += int(data.decode().split()[0])

    return count - await mails_count()


async def get_all_mails_id(server_list: list[IMAP4_SSL]) -> 'AsyncGenerator[RawMailsSchema]':
    '''
    Function to get all mails in all folders

    :param server_list: list[IMAP4_SSL]

    :return AsyncGenerator[RawMailsSchema]: Mail object
    '''

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


async def handle_and_get_mails(raw_mails: list[RawMailsSchema]):
    '''
    Function to handle all raw mails,
    check in database and return handled mails

    :param raw_mails: list[RawMailsSchema]
    '''

    old_folder = None

    for raw_mail in raw_mails:

        if await get_mail_by_id(mail_id=raw_mail.id):
            continue

        folder = await get_or_create_folder(
            name=raw_mail.folder,
            server=await get_server_by_host(
                host=raw_mail.server.host
            ),
        )

        if folder != old_folder:
            result, data = await raw_mail.server.select(folder.name)

            old_folder = folder

            if result != 'OK':
                continue

        result, data = await raw_mail.server.fetch(
            message_set=str(raw_mail.id),
            message_parts='(RFC822)',
        )

        if result != 'OK':
            logging.info(f'[HANDLING {raw_mail.server.host}] {result} | {data} | {raw_mail}')
            continue

        if len(data) == 1:
            logging.info(f'[HANDLING {raw_mail.server.host}] {result} | {data} | {raw_mail}')
            continue

        date, sender, theme, text, attachments = get_mail_data(
            mail_id=raw_mail.id,
            mail_data=data[1],
        )

        mail = await create_mail(
            mail_id=raw_mail.id,
            folder=folder,
            sender=sender,
            text=text,
            theme=theme,
            sending_date=date,
            receiving_date=date,
        )

        attachment_urls = []

        for attachment in attachments:
            attachment = await create_attachment(file=attachment, mail=mail)

            attachment_urls.append(
                attachment.file
            )

        yield mail, attachment_urls


__all__ = (
    'get_imap_servers',
    'get_all_mails_id',
    'get_mails_count',
    'handle_and_get_mails',
)
