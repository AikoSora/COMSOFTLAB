from django.core.serializers import serialize

from channels.generic.websocket import AsyncWebsocketConsumer

from ujson import loads, dumps


class EmailConsumer(AsyncWebsocketConsumer):

    async def receive(self, text_data):
        from mail.services import (
            get_all_mails_id,
            get_mails_count,
            handle_and_get_mails,
            get_imap_servers,
        )

        try:
            text_data_json = loads(text_data)
        except Exception:
            await self.send(text_data='Goodbye!', close=True)

        data = text_data_json.get('action', None)

        if data == 'update':

            servers = await get_imap_servers()

            await self.send(
                text_data=dumps(dict(
                    action='length',
                    message=await get_mails_count(
                        server_list=servers
                    )
                )),
            )

            mails = [x async for x in get_all_mails_id(server_list=servers)]

            async for mail, attachments in handle_and_get_mails(raw_mails=mails):
                await self.send(
                    text_data=dumps(dict(
                        action='email',
                        message=dict(
                            mail=serialize(
                                format='json',
                                queryset=[mail],
                            ),
                            attachments=attachments,
                        ),
                    )),
                )

            for server in servers:
                await server.close()

            await self.send(
                text_data=dumps(dict(
                    action='close',
                )),
            )


__all__ = (
    'EmailConsumer',
)
