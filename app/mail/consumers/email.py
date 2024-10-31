from channels.generic.websocket import AsyncWebsocketConsumer

from ujson import loads, dumps


class EmailConsumer(AsyncWebsocketConsumer):

    async def receive(self, text_data):
        from mail.services import get_all_mails

        try:
            text_data_json = loads(text_data)
        except Exception as ex:
            await self.send(text_data='Goodbye!', close=True)

        data = text_data_json.get('action', None)

        if data == 'update':
            mails = [x async for x in get_all_mails()]

            await self.send(
                text_data=dumps(dict(
                    action='length',
                    message=len(mails)
                ))
            )


__all__ = (
    'EmailConsumer',
)
